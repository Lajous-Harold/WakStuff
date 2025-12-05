"""
Mixins et utilitaires pour les modèles.
"""
from datetime import datetime


class DictSerializable:
    """
    Mixin pour ajouter la méthode to_dict() aux modèles.
    """
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Gérer les types spéciaux
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        
        return result
    
    def to_dict_with_relations(self, *relations):
        """
        Convertit le modèle en dictionnaire avec ses relations.
        
        Args:
            *relations: Noms des relations à inclure
        """
        result = self.to_dict()
        
        for relation_name in relations:
            if hasattr(self, relation_name):
                relation_value = getattr(self, relation_name)
                
                # Si c'est une liste
                if isinstance(relation_value, list):
                    result[relation_name] = [
                        item.to_dict() if hasattr(item, 'to_dict') else str(item)
                        for item in relation_value
                    ]
                # Si c'est un objet unique
                elif relation_value is not None:
                    if hasattr(relation_value, 'to_dict'):
                        result[relation_name] = relation_value.to_dict()
                    else:
                        result[relation_name] = str(relation_value)
                else:
                    result[relation_name] = None
        
        return result
