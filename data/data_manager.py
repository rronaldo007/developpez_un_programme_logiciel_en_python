#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de données - Architecture MVC
Responsabilité : Persistance sécurisée des données en JSON
"""

import os
import json
import shutil
import time
from typing import List, Optional, Dict
from models.player import Player
from models.tournament import Tournament
from utils.file_utils import ensure_directory_exists, safe_json_save, safe_json_load


class DataManager:
    """
    Gestionnaire de persistance des données
    
    Responsabilités :
    - Sauvegarde/chargement sécurisé des joueurs et tournois
    - Gestion des fichiers avec backup automatique
    - Intégrité des données et récupération d'erreurs
    - Export/import de données
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialise le gestionnaire de données
        
        Args:
            data_dir (str): Répertoire de stockage des données
        """
        self.data_dir = data_dir
        self.players_file = os.path.join(data_dir, "players.json")
        self.tournaments_dir = os.path.join(data_dir, "tournaments")
        self.backup_dir = os.path.join(data_dir, "backups")
        
        # Créer les répertoires nécessaires
        self._init_data_directories()
        
        # Statistiques d'utilisation
        self._stats = {
            'saves_count': 0,
            'loads_count': 0,
            'errors_count': 0,
            'last_operation': None
        }
        
    def _init_data_directories(self):
        """Crée les répertoires de données s'ils n'existent pas"""
        try:
            ensure_directory_exists(self.data_dir)
            ensure_directory_exists(self.tournaments_dir)
            ensure_directory_exists(self.backup_dir)
        except Exception as e:
            raise IOError(f"Impossible de créer les répertoires de données: {e}")
            
    def save_players(self, players: List[Player]) -> bool:
        """
        Sauvegarde la liste des joueurs avec backup automatique
        
        Args:
            players (List[Player]): Liste des joueurs à sauvegarder
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            self._stats['last_operation'] = f"save_players_{len(players)}_players"
            
            # Validation des données
            if not self._validate_players_data(players):
                return False
            
            
            # Préparer les données
            players_data = []
            for player in players:
                try:
                    player_dict = player.to_dict()
                    players_data.append(player_dict)
                except Exception as e:
                    print(f"Erreur sérialisation joueur {player}: {e}")
                    self._stats['errors_count'] += 1
                    continue
            
            # Sauvegarder
            success = safe_json_save(players_data, self.players_file)
            
            if success:
                self._stats['saves_count'] += 1
                return True
            else:
                self._stats['errors_count'] += 1
                return False
                
        except Exception as e:
            print(f"Erreur sauvegarde joueurs: {e}")
            self._stats['errors_count'] += 1
            return False
            
    def load_players(self) -> List[Player]:
        """
        Charge la liste des joueurs avec récupération d'erreur
        
        Returns:
            List[Player]: Liste des joueurs chargés
        """
        try:
            self._stats['last_operation'] = "load_players"
            
            # Vérifier l'existence du fichier
            if not os.path.exists(self.players_file):
                # Essayer de récupérer depuis un backup
                backup_file = self._find_latest_backup(self.players_file)
                if backup_file:
                    print(f"Fichier principal introuvable, récupération depuis {backup_file}")
                    shutil.copy2(backup_file, self.players_file)
                else:
                    print("Aucun fichier de joueurs trouvé, création d'une liste vide.")
                    return []
            
            # Charger les données
            players_data = safe_json_load(self.players_file)
            if not players_data:
                return []
            
            # Valider et convertir
            players = []
            for i, player_data in enumerate(players_data):
                try:
                    # Validation des champs requis
                    if not self._validate_player_dict(player_data):
                        print(f"ATTENTION: Joueur {i} ignoré - données invalides")
                        continue
                        
                    player = Player.from_dict(player_data)
                    players.append(player)
                    
                except Exception as e:
                    print(f"ATTENTION: Joueur {i} ignoré lors du chargement: {e}")
                    self._stats['errors_count'] += 1
                    continue
            
            self._stats['loads_count'] += 1
            print(f"Chargement réussi: {len(players)} joueurs")
            return players
            
        except Exception as e:
            print(f"Erreur chargement joueurs: {e}")
            self._stats['errors_count'] += 1
            
            # Tentative de récupération depuis backup
            backup_file = self._find_latest_backup(self.players_file)
            if backup_file:
                try:
                    print(f"Tentative de récupération depuis {backup_file}")
                    backup_data = safe_json_load(backup_file)
                    if backup_data:
                        players = []
                        for player_data in backup_data:
                            try:
                                player = Player.from_dict(player_data)
                                players.append(player)
                            except:
                                continue
                        print(f"Récupération réussie: {len(players)} joueurs")
                        return players
                except:
                    pass
            
            return []
            
    def save_tournament(self, tournament: Tournament) -> bool:
        """
        Sauvegarde un tournoi avec validation
        
        Args:
            tournament (Tournament): Tournoi à sauvegarder
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            self._stats['last_operation'] = f"save_tournament_{tournament.id}"
            
            # Validation du tournoi
            if not self._validate_tournament_data(tournament):
                return False
            
            # Nom du fichier
            filename = f"tournament_{tournament.id}.json"
            file_path = os.path.join(self.tournaments_dir, filename)
            
            
            # Sérialiser le tournoi
            tournament_data = tournament.to_dict()
            
            # Ajouter métadonnées
            tournament_data['_metadata'] = {
                'saved_at': time.time(),
                'version': '1.0',
                'checksum': self._calculate_checksum(tournament_data)
            }
            
            # Sauvegarder
            success = safe_json_save(tournament_data, file_path)
            
            if success:
                self._stats['saves_count'] += 1
                return True
            else:
                self._stats['errors_count'] += 1
                return False
                
        except Exception as e:
            print(f"Erreur sauvegarde tournoi {tournament.id}: {e}")
            self._stats['errors_count'] += 1
            return False
            
    def load_tournament(self, tournament_id: int, players_lookup: Dict[str, Player]) -> Optional[Tournament]:
        """
        Charge un tournoi spécifique avec validation
        
        Args:
            tournament_id (int): ID du tournoi
            players_lookup (Dict[str, Player]): Dictionnaire des joueurs par ID
            
        Returns:
            Optional[Tournament]: Tournoi chargé ou None
        """
        try:
            self._stats['last_operation'] = f"load_tournament_{tournament_id}"
            
            filename = f"tournament_{tournament_id}.json"
            file_path = os.path.join(self.tournaments_dir, filename)
            
            if not os.path.exists(file_path):
                return None
                
            # Charger les données
            tournament_data = safe_json_load(file_path)
            if not tournament_data:
                return None
            
            # Vérifier l'intégrité si métadonnées présentes
            if '_metadata' in tournament_data:
                metadata = tournament_data.pop('_metadata')
                if not self._verify_checksum(tournament_data, metadata.get('checksum')):
                    print(f"ATTENTION: Checksum invalide pour le tournoi {tournament_id}")
            
            # Validation des données
            if not self._validate_tournament_dict(tournament_data):
                print(f"ERREUR: Données du tournoi {tournament_id} invalides")
                return None
                
            # Créer le tournoi
            tournament = Tournament.from_dict(tournament_data, players_lookup)
            
            self._stats['loads_count'] += 1
            return tournament
            
        except Exception as e:
            print(f"Erreur chargement tournoi {tournament_id}: {e}")
            self._stats['errors_count'] += 1
            return None
            
    def get_all_tournament_files(self) -> List[str]:
        """
        Retourne la liste des fichiers de tournois
        
        Returns:
            List[str]: Liste des chemins de fichiers
        """
        try:
            if not os.path.exists(self.tournaments_dir):
                return []
                
            files = []
            for filename in os.listdir(self.tournaments_dir):
                if (filename.startswith("tournament_") and 
                    filename.endswith(".json") and 
                    not filename.endswith(".backup")):
                    files.append(os.path.join(self.tournaments_dir, filename))
                    
            # Trier par ID de tournoi
            files.sort(key=lambda x: self._extract_tournament_id(x))
            return files
            
        except Exception as e:
            print(f"Erreur lecture répertoire tournois: {e}")
            return []
            
    def delete_tournament(self, tournament_id: int) -> bool:
        """
        Supprime un tournoi avec backup de sécurité
        
        Args:
            tournament_id (int): ID du tournoi à supprimer
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            filename = f"tournament_{tournament_id}.json"
            file_path = os.path.join(self.tournaments_dir, filename)
            
            if not os.path.exists(file_path):
                return False
                
            # Créer backup avant suppression
            
            # Supprimer le fichier
            os.remove(file_path)
            
            print(f"Tournoi {tournament_id} supprimé (backup: {backup_path})")
            return True
            
        except Exception as e:
            print(f"Erreur suppression tournoi {tournament_id}: {e}")
            return False
            
    def export_all_data(self, export_path: str) -> bool:
        """
        Exporte toutes les données vers un fichier unique
        
        Args:
            export_path (str): Chemin du fichier d'export
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Charger toutes les données
            players = self.load_players()
            tournaments_data = []
            
            for file_path in self.get_all_tournament_files():
                tournament_data = safe_json_load(file_path)
                if tournament_data:
                    tournaments_data.append(tournament_data)
            
            # Créer le package d'export
            export_data = {
                "export_info": {
                    "timestamp": time.time(),
                    "version": "1.0",
                    "source": "Chess Tournament Manager"
                },
                "players": [player.to_dict() for player in players],
                "tournaments": tournaments_data,
                "metadata": {
                    "players_count": len(players),
                    "tournaments_count": len(tournaments_data),
                    "total_size_mb": self._calculate_total_size_mb()
                }
            }
            
            # Sauvegarder
            success = safe_json_save(export_data, export_path)
            
            if success:
                print(f"Export réussi vers {export_path}")
                return True
            else:
                print(f"Erreur lors de l'export vers {export_path}")
                return False
                
        except Exception as e:
            print(f"Erreur export: {e}")
            return False
            
    def import_all_data(self, import_path: str, merge: bool = False) -> bool:
        """
        Importe des données depuis un fichier d'export
        
        Args:
            import_path (str): Chemin du fichier d'import
            merge (bool): Si True, fusionne avec les données existantes
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            if not os.path.exists(import_path):
                print(f"Fichier d'import introuvable: {import_path}")
                return False
                
            # Charger les données d'import
            import_data = safe_json_load(import_path)
            if not import_data:
                print("Données d'import invalides")
                return False
                
            # Valider la structure
            if not all(key in import_data for key in ["players", "tournaments"]):
                print("Structure d'import invalide")
                return False
                
            # Créer backup complet avant import
            if not merge:
                self._create_full_backup()
            
            # Importer les joueurs
            players_data = import_data["players"]
            if merge:
                existing_players = self.load_players()
                existing_ids = {p.national_id for p in existing_players}
                
                # Fusionner les joueurs
                new_players = []
                for player_data in players_data:
                    if player_data.get("national_id") not in existing_ids:
                        try:
                            player = Player.from_dict(player_data)
                            new_players.append(player)
                        except:
                            continue
                
                all_players = existing_players + new_players
            else:
                # Remplacer tous les joueurs
                all_players = []
                for player_data in players_data:
                    try:
                        player = Player.from_dict(player_data)
                        all_players.append(player)
                    except:
                        continue
            
            # Sauvegarder les joueurs
            if not self.save_players(all_players):
                print("Erreur sauvegarde des joueurs importés")
                return False
            
            # Importer les tournois
            players_lookup = {p.national_id: p for p in all_players}
            imported_tournaments = 0
            
            for tournament_data in import_data["tournaments"]:
                try:
                    # Nettoyer les métadonnées d'export
                    if '_metadata' in tournament_data:
                        del tournament_data['_metadata']
                        
                    tournament = Tournament.from_dict(tournament_data, players_lookup)
                    
                    if merge:
                        # Vérifier si le tournoi existe déjà
                        existing_file = os.path.join(self.tournaments_dir, f"tournament_{tournament.id}.json")
                        if os.path.exists(existing_file):
                            continue  # Skip existing tournaments
                    
                    if self.save_tournament(tournament):
                        imported_tournaments += 1
                        
                except Exception as e:
                    print(f"Erreur import tournoi: {e}")
                    continue
            
            print(f"Import réussi: {len(all_players)} joueurs, {imported_tournaments} tournois")
            return True
            
        except Exception as e:
            print(f"Erreur import: {e}")
            return False
            
    def get_data_info(self) -> Dict:
        """
        Retourne des informations sur l'état des données
        
        Returns:
            Dict: Informations détaillées
        """
        try:
            info = {
                "data_directory": self.data_dir,
                "players_file": self.players_file,
                "tournaments_directory": self.tournaments_dir,
                "backup_directory": self.backup_dir
            }
            
            # Statistiques des joueurs
            if os.path.exists(self.players_file):
                info["players_file_size"] = os.path.getsize(self.players_file)
                info["players_last_modified"] = os.path.getmtime(self.players_file)
                
                try:
                    players = self.load_players()
                    info["players_count"] = len(players)
                except:
                    info["players_count"] = 0
            else:
                info["players_file_size"] = 0
                info["players_count"] = 0
            
            # Statistiques des tournois
            tournament_files = self.get_all_tournament_files()
            info["tournaments_count"] = len(tournament_files)
            info["tournaments_total_size"] = sum(
                os.path.getsize(f) for f in tournament_files if os.path.exists(f)
            )
            
            # Statistiques d'utilisation
            info["usage_stats"] = self._stats.copy()
            
            # Informations sur les backups
            backup_files = []
            if os.path.exists(self.backup_dir):
                backup_files = [f for f in os.listdir(self.backup_dir) if f.endswith('.backup')]
            info["backup_files_count"] = len(backup_files)
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
            
    def _create_backup(self, file_path: str) -> Optional[str]:
        """Crée un backup d'un fichier"""
        try:
            if not os.path.exists(file_path):
                return None
                
            timestamp = int(time.time())
            backup_filename = f"{os.path.basename(file_path)}.{timestamp}.backup"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            shutil.copy2(file_path, backup_path)
            
            # Nettoyer les anciens backups
            self._cleanup_old_backups(os.path.basename(file_path))
            
            return backup_path
            
        except Exception as e:
            print(f"Erreur création backup: {e}")
            return None
            
    def _find_latest_backup(self, file_path: str) -> Optional[str]:
        """Trouve le backup le plus récent d'un fichier"""
        try:
            if not os.path.exists(self.backup_dir):
                return None
                
            base_filename = os.path.basename(file_path)
            backup_files = []
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith(base_filename) and filename.endswith('.backup'):
                    backup_path = os.path.join(self.backup_dir, filename)
                    mtime = os.path.getmtime(backup_path)
                    backup_files.append((mtime, backup_path))
            
            if backup_files:
                # Retourner le plus récent
                backup_files.sort(reverse=True)
                return backup_files[0][1]
                
            return None
            
        except Exception:
            return None
            
    def _cleanup_old_backups(self, base_filename: str, max_backups: int = 5):
        """Nettoie les anciens backups"""
        try:
            if not os.path.exists(self.backup_dir):
                return
                
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith(base_filename) and filename.endswith('.backup'):
                    backup_path = os.path.join(self.backup_dir, filename)
                    mtime = os.path.getmtime(backup_path)
                    backup_files.append((mtime, backup_path))
            
            # Garder seulement les plus récents
            if len(backup_files) > max_backups:
                backup_files.sort(reverse=True)
                for _, old_backup in backup_files[max_backups:]:
                    try:
                        os.remove(old_backup)
                    except:
                        pass
                        
        except Exception:
            pass
            
    def _create_full_backup(self):
        """Crée un backup complet avant import"""
        try:
            timestamp = int(time.time())
            backup_name = f"full_backup_{timestamp}"
            full_backup_dir = os.path.join(self.backup_dir, backup_name)
            
            ensure_directory_exists(full_backup_dir)
            
            # Backup du fichier des joueurs
            if os.path.exists(self.players_file):
                shutil.copy2(self.players_file, os.path.join(full_backup_dir, "players.json"))
            
            # Backup du répertoire des tournois
            if os.path.exists(self.tournaments_dir):
                tournaments_backup = os.path.join(full_backup_dir, "tournaments")
                shutil.copytree(self.tournaments_dir, tournaments_backup)
                
            print(f"Backup complet créé: {full_backup_dir}")
            
        except Exception as e:
            print(f"Erreur création backup complet: {e}")
            
    def _validate_players_data(self, players: List[Player]) -> bool:
        """Valide une liste de joueurs"""
        try:
            if not isinstance(players, list):
                return False
                
            # Vérifier l'unicité des IDs
            seen_ids = set()
            for player in players:
                if not isinstance(player, Player):
                    return False
                if player.national_id in seen_ids:
                    print(f"ERREUR: ID dupliqué détecté: {player.national_id}")
                    return False
                seen_ids.add(player.national_id)
                
            return True
            
        except Exception:
            return False
            
    def _validate_player_dict(self, player_data: Dict) -> bool:
        """Valide un dictionnaire de joueur"""
        required_fields = ["last_name", "first_name", "birthdate", "national_id"]
        return all(field in player_data and player_data[field] for field in required_fields)
        
    def _validate_tournament_data(self, tournament: Tournament) -> bool:
        """Valide un tournoi"""
        try:
            if not isinstance(tournament, Tournament):
                return False
            if not tournament.name or not tournament.location:
                return False
            return True
        except Exception:
            return False
            
    def _validate_tournament_dict(self, tournament_data: Dict) -> bool:
        """Valide un dictionnaire de tournoi"""
        required_fields = ["id", "name", "location", "start_date", "end_date"]
        return all(field in tournament_data for field in required_fields)
        
    def _extract_tournament_id(self, file_path: str) -> int:
        """Extrait l'ID d'un fichier de tournoi"""
        try:
            filename = os.path.basename(file_path)
            id_str = filename.replace("tournament_", "").replace(".json", "")
            return int(id_str)
        except:
            return 0
            
    def _calculate_checksum(self, data: Dict) -> str:
        """Calcule un checksum simple pour vérifier l'intégrité"""
        try:
            import hashlib
            data_str = json.dumps(data, sort_keys=True)
            return hashlib.md5(data_str.encode()).hexdigest()
        except:
            return ""
            
    def _verify_checksum(self, data: Dict, expected_checksum: str) -> bool:
        """Vérifie un checksum"""
        if not expected_checksum:
            return True  # Pas de checksum à vérifier
        return self._calculate_checksum(data) == expected_checksum
        
    def _calculate_total_size_mb(self) -> float:
        """Calcule la taille totale des données en MB"""
        try:
            total_size = 0
            
            # Taille du fichier des joueurs
            if os.path.exists(self.players_file):
                total_size += os.path.getsize(self.players_file)
            
            # Taille des tournois
            for file_path in self.get_all_tournament_files():
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
            
            return round(total_size / (1024 * 1024), 2)
            
        except:
            return 0.0
            
    def optimize_data_files(self) -> Dict:
        """
        Optimise les fichiers de données (compactage, nettoyage)
        
        Returns:
            Dict: Résultats de l'optimisation
        """
        results = {
            'players_optimized': False,
            'tournaments_optimized': 0,
            'space_saved_mb': 0.0,
            'errors': []
        }
        
        try:
            original_size = self._calculate_total_size_mb()
            
            # Optimiser le fichier des joueurs
            try:
                players = self.load_players()
                if players:
                    # Re-sauvegarder pour compacter
                    if self.save_players(players):
                        results['players_optimized'] = True
            except Exception as e:
                results['errors'].append(f"Erreur optimisation joueurs: {e}")
            
            # Optimiser les tournois
            tournament_files = self.get_all_tournament_files()
            players_lookup = {p.national_id: p for p in self.load_players()}
            
            for file_path in tournament_files:
                try:
                    tournament_id = self._extract_tournament_id(file_path)
                    tournament = self.load_tournament(tournament_id, players_lookup)
                    
                    if tournament:
                        # Re-sauvegarder pour compacter
                        if self.save_tournament(tournament):
                            results['tournaments_optimized'] += 1
                            
                except Exception as e:
                    results['errors'].append(f"Erreur optimisation tournoi {file_path}: {e}")
            
            # Calculer l'espace économisé
            new_size = self._calculate_total_size_mb()
            results['space_saved_mb'] = max(0, original_size - new_size)
            
            # Nettoyer les fichiers temporaires
            self._cleanup_temp_files()
            
        except Exception as e:
            results['errors'].append(f"Erreur générale optimisation: {e}")
        
        return results
        
    def _cleanup_temp_files(self):
        """Nettoie les fichiers temporaires"""
        try:
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    if file.endswith('.tmp') or file.endswith('.temp'):
                        try:
                            os.remove(os.path.join(root, file))
                        except:
                            pass
        except:
            pass
            
    def verify_data_integrity(self) -> Dict:
        """
        Vérifie l'intégrité de toutes les données
        
        Returns:
            Dict: Rapport d'intégrité
        """
        report = {
            'players_integrity': True,
            'tournaments_integrity': True,
            'players_errors': [],
            'tournaments_errors': [],
            'missing_files': [],
            'corrupted_files': [],
            'orphaned_references': []
        }
        
        try:
            # Vérifier les joueurs
            try:
                players = self.load_players()
                
                # Vérifier l'unicité des IDs
                seen_ids = set()
                for i, player in enumerate(players):
                    if player.national_id in seen_ids:
                        report['players_errors'].append(f"ID dupliqué: {player.national_id}")
                        report['players_integrity'] = False
                    seen_ids.add(player.national_id)
                    
                    # Vérifier la validité des données
                    try:
                        player.calculate_age()  # Test de validité de la date
                    except:
                        report['players_errors'].append(f"Date invalide pour {player.national_id}")
                        
            except Exception as e:
                report['players_integrity'] = False
                report['players_errors'].append(f"Erreur chargement: {e}")
            
            # Vérifier les tournois
            players_lookup = {p.national_id: p for p in self.load_players()}
            tournament_files = self.get_all_tournament_files()
            
            for file_path in tournament_files:
                try:
                    tournament_id = self._extract_tournament_id(file_path)
                    tournament = self.load_tournament(tournament_id, players_lookup)
                    
                    if not tournament:
                        report['corrupted_files'].append(file_path)
                        report['tournaments_integrity'] = False
                        continue
                    
                    # Vérifier les références aux joueurs
                    for player in tournament.players:
                        if player.national_id not in players_lookup:
                            report['orphaned_references'].append(
                                f"Tournoi {tournament_id}: joueur {player.national_id} introuvable"
                            )
                    
                    # Vérifier la cohérence des matchs
                    for round_obj in tournament.rounds:
                        for match in round_obj.matches:
                            if (match.player1_national_id not in players_lookup or
                                match.player2_national_id not in players_lookup):
                                report['orphaned_references'].append(
                                    f"Tournoi {tournament_id}: référence joueur invalide dans match"
                                )
                                
                except Exception as e:
                    report['tournaments_errors'].append(f"Erreur tournoi {file_path}: {e}")
                    report['tournaments_integrity'] = False
            
            # Vérifier les fichiers manquants
            expected_files = [self.players_file]
            for file_path in expected_files:
                if not os.path.exists(file_path):
                    report['missing_files'].append(file_path)
            
        except Exception as e:
            report['general_error'] = str(e)
        
        return report
        
    def repair_data_integrity(self) -> Dict:
        """
        Tente de réparer les problèmes d'intégrité des données
        
        Returns:
            Dict: Résultats de la réparation
        """
        results = {
            'repaired_players': 0,
            'repaired_tournaments': 0,
            'removed_duplicates': 0,
            'fixed_references': 0,
            'errors': []
        }
        
        try:
            # Créer un backup avant réparation
            self._create_full_backup()
            
            # Réparer les joueurs
            try:
                players = self.load_players()
                
                # Supprimer les doublons
                seen_ids = set()
                unique_players = []
                
                for player in players:
                    if player.national_id not in seen_ids:
                        unique_players.append(player)
                        seen_ids.add(player.national_id)
                    else:
                        results['removed_duplicates'] += 1
                
                if self.save_players(unique_players):
                    results['repaired_players'] = len(unique_players)
                    
            except Exception as e:
                results['errors'].append(f"Erreur réparation joueurs: {e}")
            
            # Réparer les tournois
            players_lookup = {p.national_id: p for p in self.load_players()}
            tournament_files = self.get_all_tournament_files()
            
            for file_path in tournament_files:
                try:
                    tournament_data = safe_json_load(file_path)
                    if not tournament_data:
                        continue
                    
                    # Nettoyer les références invalides
                    repaired = False
                    
                    # Nettoyer les joueurs du tournoi
                    if 'players' in tournament_data:
                        valid_players = []
                        for player_data in tournament_data['players']:
                            player_id = player_data.get('national_id')
                            if player_id and player_id in players_lookup:
                                valid_players.append(player_data)
                            else:
                                repaired = True
                                results['fixed_references'] += 1
                        
                        tournament_data['players'] = valid_players
                    
                    # Nettoyer les matchs
                    if 'rounds' in tournament_data:
                        for round_data in tournament_data['rounds']:
                            if 'matches' in round_data:
                                valid_matches = []
                                for match_data in round_data['matches']:
                                    p1_id = match_data.get('player1_national_id')
                                    p2_id = match_data.get('player2_national_id')
                                    
                                    if (p1_id in players_lookup and 
                                        p2_id in players_lookup):
                                        valid_matches.append(match_data)
                                    else:
                                        repaired = True
                                        results['fixed_references'] += 1
                                
                                round_data['matches'] = valid_matches
                    
                    # Sauvegarder si réparé
                    if repaired:
                        if safe_json_save(tournament_data, file_path):
                            results['repaired_tournaments'] += 1
                            
                except Exception as e:
                    results['errors'].append(f"Erreur réparation tournoi {file_path}: {e}")
            
        except Exception as e:
            results['errors'].append(f"Erreur générale réparation: {e}")
        
        return results