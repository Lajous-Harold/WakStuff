"""
Interface visuelle de test pour le système d'import Wakfu.
"""

from flask import Blueprint, render_template_string, jsonify
from ..database import db
from ..models import Item, ItemCategory, Recipe, Action, State, Job

test_views_bp = Blueprint("test_views", __name__, url_prefix="/test")


@test_views_bp.get("/")
def test_dashboard():
    """Page HTML de test avec tous les outils."""
    
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WakStuff - Interface de Test</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            h1 {
                color: white;
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .section {
                background: white;
                border-radius: 12px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .section h2 {
                color: #667eea;
                margin-bottom: 15px;
                font-size: 1.5em;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            
            .button-group {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-bottom: 15px;
            }
            
            button {
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            .output {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 15px;
                max-height: 500px;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            
            .status {
                padding: 8px 16px;
                border-radius: 6px;
                margin: 10px 0;
                font-weight: 600;
            }
            
            .status.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            
            .status.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            
            .status.info {
                background: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }
            
            .loading {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 3px solid rgba(255,255,255,.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            .input-group {
                margin: 15px 0;
            }
            
            .input-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
                color: #495057;
            }
            
            .input-group input, .input-group select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 14px;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 15px 0;
            }
            
            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }
            
            .stat-card .number {
                font-size: 2em;
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .stat-card .label {
                font-size: 0.9em;
                opacity: 0.9;
            }
            
            .item-card {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                transition: box-shadow 0.2s;
            }
            
            .item-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            
            .item-card h3 {
                color: #667eea;
                margin-bottom: 10px;
            }
            
            .item-card .category {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
                margin-right: 8px;
            }
            
            .item-card .level {
                display: inline-block;
                background: #764ba2;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>WakStuff - Interface de Test</h1>
            
            <div class="section">
                <h2>Import des Données Wakfu</h2>
                <div class="button-group">
                    <button onclick="runFullImport()">
                        <span id="import-spinner" style="display:none" class="loading"></span>
                        Lancer Import Complet
                    </button>
                </div>
                <div id="import-status"></div>
                <div id="import-output" class="output" style="display:none;"></div>
            </div>
            
            <div class="section">
                <h2>Statistiques</h2>
                <div class="button-group">
                    <button onclick="loadStats()">Charger les Statistiques</button>
                </div>
                <div id="stats-container"></div>
            </div>
            
            <div class="section">
                <h2>Catégories d'Items</h2>
                <div class="button-group">
                    <button onclick="loadCategories()">Charger les Catégories</button>
                </div>
                <div id="categories-output" class="output" style="display:none;"></div>
            </div>
            
            <div class="section">
                <h2>Items</h2>
                <div class="input-group">
                    <label for="category-filter">Filtrer par catégorie:</label>
                    <select id="category-filter">
                        <option value="">Toutes les catégories</option>
                    </select>
                </div>
                <div class="button-group">
                    <button onclick="loadItems()">Charger Items (20 premiers)</button>
                    <button onclick="loadItemsDetailed()">Charger Items Détaillés</button>
                </div>
                <div id="items-output"></div>
            </div>
            
            <div class="section">
                <h2>Calculateur de Craft</h2>
                <div class="input-group">
                    <label for="craft-item-id">ID de l'item à crafter:</label>
                    <input type="number" id="craft-item-id" placeholder="Ex: 12345">
                </div>
                <div class="input-group">
                    <label for="craft-quantity">Quantité:</label>
                    <input type="number" id="craft-quantity" value="1" min="1">
                </div>
                <div class="button-group">
                    <button onclick="calculateCraft()">Calculer Ressources</button>
                </div>
                <div id="craft-output" class="output" style="display:none;"></div>
            </div>
        </div>
        
        <script>
            // Configuration
            const API_BASE = '/api';
            
            // Helper: Afficher un message de status
            function showStatus(elementId, message, type = 'info') {
                const el = document.getElementById(elementId);
                el.innerHTML = `<div class="status ${type}">${message}</div>`;
            }
            
            function showError(elementId, error) {
                console.error(error);
                showStatus(elementId, `Erreur: ${error.message || error}`, 'error');
            }
            
            async function runFullImport() {
                const btn = event.target;
                const spinner = document.getElementById('import-spinner');
                const statusDiv = document.getElementById('import-status');
                const outputDiv = document.getElementById('import-output');
                
                btn.disabled = true;
                spinner.style.display = 'inline-block';
                showStatus('import-status', 'Import en cours... Cela peut prendre plusieurs minutes.', 'info');
                outputDiv.style.display = 'none';
                
                try {
                    const response = await fetch(`${API_BASE}/wakfu/import/full`, {
                        method: 'POST'
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    showStatus('import-status', 'Import terminé avec succès!', 'success');
                    outputDiv.textContent = JSON.stringify(data, null, 2);
                    outputDiv.style.display = 'block';
                } catch (error) {
                    showError('import-status', error);
                } finally {
                    btn.disabled = false;
                    spinner.style.display = 'none';
                }
            }
            
            async function loadStats() {
                const container = document.getElementById('stats-container');
                container.innerHTML = '<div class="status info">Chargement...</div>';
                
                try {
                    const response = await fetch(`${API_BASE}/wakfu/stats`);
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    
                    const data = await response.json();
                    
                    let html = '<div class="stats-grid">';
                    html += `
                        <div class="stat-card">
                            <div class="number">${data.total_items || 0}</div>
                            <div class="label">Items</div>
                        </div>
                        <div class="stat-card">
                            <div class="number">${data.total_recipes || 0}</div>
                            <div class="label">Recettes</div>
                        </div>
                        <div class="stat-card">
                            <div class="number">${data.total_categories || 0}</div>
                            <div class="label">Catégories</div>
                        </div>
                        <div class="stat-card">
                            <div class="number">${data.total_actions || 0}</div>
                            <div class="label">Actions</div>
                        </div>
                        <div class="stat-card">
                            <div class="number">${data.total_states || 0}</div>
                            <div class="label">États</div>
                        </div>
                        <div class="stat-card">
                            <div class="number">${data.total_jobs || 0}</div>
                            <div class="label">Métiers</div>
                        </div>
                    `;
                    html += '</div>';
                    
                    if (data.items_by_category && Object.keys(data.items_by_category).length > 0) {
                        html += '<h3 style="margin-top: 20px;">Items par catégorie:</h3>';
                        html += '<div class="output">';
                        for (const [cat, count] of Object.entries(data.items_by_category)) {
                            html += `${cat}: ${count}\\n`;
                        }
                        html += '</div>';
                    }
                    
                    container.innerHTML = html;
                } catch (error) {
                    container.innerHTML = `<div class="status error">Erreur: ${error.message}</div>`;
                }
            }
            
            async function loadCategories() {
                const output = document.getElementById('categories-output');
                output.style.display = 'block';
                output.textContent = 'Chargement...';
                
                try {
                    const response = await fetch(`${API_BASE}/wakfu/categories`);
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    
                    const data = await response.json();
                    output.textContent = JSON.stringify(data, null, 2);
                    
                    // Peupler le select de filtrage
                    const select = document.getElementById('category-filter');
                    select.innerHTML = '<option value="">Toutes les catégories</option>';
                    data.categories.forEach(cat => {
                        const option = document.createElement('option');
                        option.value = cat.name;
                        option.textContent = `${cat.name} (${cat.item_count})`;
                        select.appendChild(option);
                    });
                } catch (error) {
                    output.textContent = `Erreur: ${error.message}`;
                }
            }
            
            async function loadItems(detailed = false) {
                const output = document.getElementById('items-output');
                const category = document.getElementById('category-filter').value;
                
                output.innerHTML = '<div class="status info">Chargement...</div>';
                
                try {
                    let url = `${API_BASE}/items?limit=20`;
                    if (category) url += `&category=${encodeURIComponent(category)}`;
                    if (detailed) url += '&details=true';
                    
                    const response = await fetch(url);
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    
                    const data = await response.json();
                    
                    let html = `<p><strong>Total: ${data.total} items</strong> (affichage: ${data.items.length})</p>`;
                    
                    data.items.forEach(item => {
                        html += `
                            <div class="item-card">
                                <h3>${item.name}</h3>
                                <div>
                                    ${item.category ? `<span class="category">${item.category}</span>` : ''}
                                    <span class="level">Lvl ${item.level}</span>
                                </div>
                                <p style="margin-top: 10px; color: #666;">
                                    <strong>Type:</strong> ${item.type || 'N/A'} | 
                                    <strong>Rarity:</strong> ${item.rarity || 'N/A'}
                                    ${item.element ? ` | <strong>Element:</strong> ${item.element}` : ''}
                                </p>
                                ${detailed && item.parsed_effects ? `
                                    <details style="margin-top: 10px;">
                                        <summary style="cursor: pointer; color: #667eea; font-weight: 600;">
                                            Effets Parsés
                                        </summary>
                                        <pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 10px; overflow-x: auto;">${JSON.stringify(item.parsed_effects, null, 2)}</pre>
                                    </details>
                                ` : ''}
                            </div>
                        `;
                    });
                    
                    output.innerHTML = html;
                } catch (error) {
                    output.innerHTML = `<div class="status error">Erreur: ${error.message}</div>`;
                }
            }
            
            function loadItemsDetailed() {
                loadItems(true);
            }
            
            async function calculateCraft() {
                const itemId = document.getElementById('craft-item-id').value;
                const quantity = document.getElementById('craft-quantity').value || 1;
                const output = document.getElementById('craft-output');
                
                if (!itemId) {
                    output.style.display = 'block';
                    output.textContent = 'Veuillez entrer un ID d\'item';
                    return;
                }
                
                output.style.display = 'block';
                output.textContent = 'Calcul en cours...';
                
                try {
                    const response = await fetch(`${API_BASE}/wakfu/craft-calculator/${itemId}?quantity=${quantity}`);
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    
                    const data = await response.json();
                    output.textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    output.textContent = `Erreur: ${error.message}`;
                }
            }{
                loadCategories();
            });
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html)
