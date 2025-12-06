"""
Mixins et utilitaires pour les modèles.
"""
from datetime import datetime


class DictSerializable:
    """
    Mixin pour ajouter la méthode to_dict() aux modèles.
    """
    
    def to_dict(self, lang='fr'):
        """
        Convertit le modèle en dictionnaire.
        
        Args:
            lang: Langue à extraire pour les champs multilingues (défaut: 'fr')
        """
        result = {}
        
        # Liste des champs connus comme multilingues
        multilingual_fields = ['title', 'description', 'name']
        
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Gérer les types spéciaux
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, dict) and column.name in multilingual_fields:
                # Extraire la langue demandée pour les champs multilingues
                # Priorité: lang demandée > 'fr' > 'en' > première clé disponible
                result[column.name] = (
                    value.get(lang) or 
                    value.get('fr') or 
                    value.get('en') or 
                    next(iter(value.values())) if value else ''
                )
            else:
                result[column.name] = value
        
        return result
    
    def to_dict_with_relations(self, *relations, lang='fr'):
        """
        Convertit le modèle en dictionnaire avec ses relations.
        
        Args:
            *relations: Noms des relations à inclure
            lang: Langue à extraire pour les champs multilingues (défaut: 'fr')
        """
        result = self.to_dict(lang=lang)
        
        for relation_name in relations:
            if hasattr(self, relation_name):
                relation_value = getattr(self, relation_name)
                
                # Si c'est une liste
                if isinstance(relation_value, list):
                    result[relation_name] = [
                        item.to_dict(lang=lang) if hasattr(item, 'to_dict') else str(item)
                        for item in relation_value
                    ]
                # Si c'est un objet unique
                elif relation_value is not None:
                    if hasattr(relation_value, 'to_dict'):
                        result[relation_name] = relation_value.to_dict(lang=lang)
                    else:
                        result[relation_name] = str(relation_value)
                else:
                    result[relation_name] = None
        
        return result
