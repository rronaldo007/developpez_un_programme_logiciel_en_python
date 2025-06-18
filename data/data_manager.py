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
        