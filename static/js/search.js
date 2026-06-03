/**
 * Script JavaScript pour la recherche et l'autocomplétion
 * ========================================================
 * Ce fichier gère :
 * - La recherche en temps réel
 * - L'autocomplétion pendant la saisie
 * - L'affichage des résultats
 * - La gestion des événements clavier (notamment la barre d'espace)
 */

// ============================================================================
// VARIABLES GLOBALES
// ============================================================================

// Référence à l'élément input de recherche
const searchInput = document.getElementById('searchInput');

// Référence à la liste d'autocomplétion
const autocompleteList = document.getElementById('autocompleteList');

// Référence aux conteneurs de résultats (un pour chaque type de recherche)
const classicResultsContainer = document.getElementById('classicResultsContainer');
const vectorResultsContainer = document.getElementById('vectorResultsContainer');

// Référence aux messages de chargement
const loadingMessage = document.getElementById('loadingMessage');
const vectorLoadingMessage = document.getElementById('vectorLoadingMessage');

// Référence au bouton de recherche
const searchButton = document.getElementById('searchButton');

// Référence à la zone de recherche vectorielle ML
const vectorSearchInput = document.getElementById('vectorSearchInput');
const vectorSearchButton = document.getElementById('vectorSearchButton');

// Variable pour stocker le délai de l'autocomplétion (debounce)
let autocompleteTimeout = null;

// ============================================================================
// FONCTION : Récupération des suggestions d'autocomplétion
// ============================================================================

/**
 * Récupère les suggestions d'autocomplétion depuis l'API Flask.
 * 
 * Cette fonction envoie une requête à /api/autocomplete pour obtenir
 * une liste de titres correspondant à la recherche.
 * 
 * @param {string} query - Le terme de recherche
 */
async function fetchAutocomplete(query) {
    try {
        // Construction de l'URL avec le paramètre de recherche
        const url = `/api/autocomplete?query=${encodeURIComponent(query)}`;
        // encodeURIComponent : encode les caractères spéciaux pour l'URL
        
        // Envoi de la requête HTTP GET
        const response = await fetch(url);
        // fetch : API moderne pour les requêtes HTTP (remplace XMLHttpRequest)
        
        // Conversion de la réponse en JSON
        const data = await response.json();
        
        // Si la requête a réussi, afficher les suggestions
        if (data.success) {
            displayAutocomplete(data.titles);
        }
        
    } catch (error) {
        // Gestion des erreurs (réseau, serveur, etc.)
        console.error('Erreur lors de l\'autocomplétion:', error);
    }
}

// ============================================================================
// FONCTION : Affichage de la liste d'autocomplétion
// ============================================================================

/**
 * Affiche les suggestions d'autocomplétion dans la liste déroulante.
 * 
 * @param {Array<string>} titles - Liste des titres à afficher
 */
/**
 * Affiche les titres dans une liste sous la zone de recherche (autocomplétion).
 * Cas b) : Les premiers titres correspondants apparaissent automatiquement.
 * Cas c) : Une fois qu'un mot est choisi, la page met à jour les informations.
 */
function displayAutocomplete(titles) {
    // Vider la liste actuelle
    autocompleteList.innerHTML = '';
    
    // Si aucun titre n'est trouvé, cacher la liste
    if (titles.length === 0) {
        autocompleteList.classList.remove('show');
        return;
    }
    
    console.log(`Affichage de ${titles.length} suggestions d'autocomplétion`);
    
    // Créer un élément <li> pour chaque titre
    // Les titres sont affichés dans une liste sous la zone de recherche
    titles.forEach((title, index) => {
        const li = document.createElement('li');
        li.className = 'autocomplete-item';
        li.textContent = title;
        
        // Améliorer l'affichage visuel avec un numéro
        if (index < 9) {
            li.setAttribute('data-index', index + 1);
        }
        
        // Événement : clic sur une suggestion
        // Cas c) : Une fois qu'un mot est choisi, la page doit mettre à jour les informations
        li.addEventListener('click', (e) => {
            // Empêcher la propagation pour éviter de fermer immédiatement
            e.stopPropagation();
            
            console.log(`✅ Titre sélectionné: "${title}"`);
            
            // Extraire juste le terme de recherche principal de la suggestion
            // Par exemple, de "ID 166 - Ahmedabad - Student (BA)" extraire "Ahmedabad"
            const parts = title.split(' - ');
            let searchTerm = parts.length > 1 ? parts[1] : title;
            
            // Remplir l'input avec le terme de recherche
            searchInput.value = searchTerm;
            
            // Cacher la liste d'autocomplétion
            autocompleteList.classList.remove('show');
            
            // Cas c) : Mettre à jour les informations en lançant la recherche
            // La page doit mettre à jour les informations automatiquement
            performSearch(searchTerm, true);  // true = avec scroll automatique vers les résultats
        });
        
        // Ajouter l'élément à la liste
        autocompleteList.appendChild(li);
    });
    
    // Afficher la liste sous la zone de recherche
    autocompleteList.classList.add('show');
    console.log('Liste d\'autocomplétion affichée');
}

// ============================================================================
// FONCTION : Recherche de documents
// ============================================================================

/**
 * Effectue une recherche de documents et affiche les résultats.
 * 
 * Cette fonction gère les cas suivants selon les spécifications :
 * - Cas a) Query vide ou espace : affiche les 10 premiers documents automatiquement
 * - Cas b) Query avec texte : recherche les documents correspondants
 * - Cas c) Une fois qu'un mot est choisi (via autocomplétion ou recherche), 
 *          la page met à jour les informations automatiquement
 * 
 * Après la recherche, scroll automatiquement vers la section des résultats.
 * 
 * @param {string} query - Le terme de recherche
 * @param {boolean} autoScroll - Si true, scroll vers résultats (défaut: true)
 */
async function performSearch(query, autoScroll = true) {
    try {
        // Scroll vers la section de recherche classique SEULEMENT si demandé
        if (autoScroll) {
            scrollToSection('classic-search');
            console.log('Redirection automatique vers la recherche classique');
        }
        
        // Afficher le message de chargement
        if (loadingMessage) loadingMessage.style.display = 'block';
        if (classicResultsContainer) classicResultsContainer.innerHTML = '';
        
        // Construction de l'URL avec le paramètre de recherche
        const url = `/api/search?query=${encodeURIComponent(query)}`;
        
        // Envoi de la requête HTTP GET
        const response = await fetch(url);
        
        // Conversion de la réponse en JSON
        const data = await response.json();
        
        // Cacher le message de chargement
        if (loadingMessage) loadingMessage.style.display = 'none';
        
        // Si la requête a réussi, afficher les résultats
        if (data.success) {
            displayResults(data.results, classicResultsContainer);
        } else {
            // Afficher un message d'erreur
            if (classicResultsContainer) {
                classicResultsContainer.innerHTML = `
                    <div class="error-message">
                        <p>Erreur lors de la recherche : ${data.error || 'Erreur inconnue'}</p>
                    </div>
                `;
            }
        }
        
    } catch (error) {
        // Gestion des erreurs
        if (loadingMessage) loadingMessage.style.display = 'none';
        console.error('Erreur lors de la recherche:', error);
        if (classicResultsContainer) {
            classicResultsContainer.innerHTML = `
                <div class="error-message">
                    <p>Erreur de connexion au serveur. Vérifiez votre connexion.</p>
                </div>
            `;
        }
    }
}

// ============================================================================
// FONCTION : Affichage des résultats
// ============================================================================

/**
 * Affiche les résultats de recherche dans le conteneur.
 * 
 * Cette fonction crée des cartes pour chaque document trouvé,
 * en affichant au moins 5 champs (titre, année, réalisateur, genre, résumé).
 * 
 * @param {Array<Object>} results - Liste des documents trouvés
 * @param {HTMLElement} container - Conteneur où afficher les résultats (optionnel, défaut: classicResultsContainer)
 */
function displayResults(results, container = null) {
    // Utiliser le conteneur fourni ou le conteneur classique par défaut
    const targetContainer = container || classicResultsContainer;
    
    if (!targetContainer) {
        console.error('Conteneur de résultats non trouvé');
        return;
    }
    
    // Si aucun résultat, afficher un message
    if (results.length === 0) {
        targetContainer.innerHTML = `
            <p class="empty-message">Aucun résultat trouvé pour votre recherche.</p>
        `;
        return;
    }
    
    // Vider le conteneur
    targetContainer.innerHTML = '';
    
    // Ajouter un compteur de résultats en haut
    const countDiv = document.createElement('div');
    countDiv.className = 'results-count';
    countDiv.style.cssText = 'text-align: center; padding: 15px; background: #f0f0f0; border-radius: 10px; margin-bottom: 20px; font-weight: bold; color: #667eea;';
    countDiv.innerHTML = `<strong>${results.length}</strong> étudiant(s) trouvé(s)`;
    targetContainer.appendChild(countDiv);
    
    // Créer une carte pour chaque résultat
    results.forEach(doc => {
        // Création de l'élément carte
        const card = document.createElement('div');
        card.className = 'result-card';
        
        // Extraction des champs du document étudiant
        // Utilisation des noms de champs en anglais de la base de données
        const cleanValue = (val) => {
            if (val === null || val === undefined) return 'Non spécifié';
            const str = String(val).trim();
            return str.replace(/^["']|["']$/g, ''); // Enlever guillemets au début/fin
        };
        
        // Mapping des champs de la base de données (en anglais) vers les variables
        const identifiant = doc.id || doc.identifiant || 'N/A';
        const genre = cleanValue(doc.gender || doc.genre || doc.Genre);
        const age = doc.age || doc.âge || 'Non spécifié';
        const ville = cleanValue(doc.city || doc.ville || doc.Ville);
        const profession = cleanValue(doc.profession || doc.Profession);
        const degre = cleanValue(doc.degree || doc.degré || doc.degre || doc.Degré);
        const moyenne = doc.cgpa || doc['moyenne cumulative'] || doc.moyenne_cumulative || 'N/A';
        const pressionAcademique = doc.academicPressure || doc['Pression académique'] || doc.pression_academique || 'N/A';
        const satisfactionEtudes = doc.studySatisfaction || doc['satisfaction des études'] || doc.satisfaction_etudes || 'N/A';
        const dureeSommeil = cleanValue(doc.sleepDuration || doc['durée du sommeil'] || doc.duree_sommeil);
        const habitudesAlimentaires = cleanValue(doc.dietaryHabits || doc['Habitudes alimentaires'] || doc.habitudes_alimentaires);
        const penseesSuicidaires = cleanValue(doc.suicidalThoughts || doc['Pensées suicidaires'] || doc.pensees_suicidaires);
        const stressFinancier = doc.financialStress || doc['Stress financier'] || doc.stress_financier || 'N/A';
        const depression = doc.depression || doc.dépression || 'N/A';
        const antecedentsFamiliaux = cleanValue(doc.familyHistoryMentalIllness || doc['Antécédents familiaux et maladie mentale'] || doc.antecedents_familiaux);
        
        // Déterminer les classes de statut pour certaines valeurs
        const getStatusClass = (field, value) => {
            if (field === 'depression' && value === 0) return 'status-positive';
            if (field === 'depression' && value === 1) return 'status-negative';
            if (field === 'suicidalThoughts' && value === 'No') return 'status-positive';
            if (field === 'suicidalThoughts' && value === 'Yes') return 'status-negative';
            if (field === 'dietaryHabits' && value === 'Healthy') return 'status-positive';
            if (field === 'dietaryHabits' && value === 'Unhealthy') return 'status-negative';
            if (field === 'cgpa' && parseFloat(value) >= 8.0) return 'status-positive';
            return '';
        };
        
        // Construction du HTML de la carte avec design professionnel
        // On affiche AU MOINS 5 champs comme demandé (garantis même si certains sont manquants)
        // Les 5 champs de base garantis : ID, Genre, Âge, Ville, Profession
        card.innerHTML = `
            <div class="card-header">
                <div class="card-header-content">
                    <h3 class="student-id">Étudiant ID: ${escapeHtml(String(identifiant))}</h3>
                    <div class="card-actions">
                        <button class="btn-similar" onclick="findSimilarStudents('${doc._id}', ${identifiant})" title="Trouver des étudiants avec un profil similaire">
                            Similaires
                        </button>
                        <button class="btn-edit" onclick="editStudent('${doc._id}')" title="Modifier les informations">
                            Modifier
                        </button>
                        <button class="btn-delete" onclick="deleteStudent('${doc._id}', ${identifiant})" title="Supprimer définitivement">
                            Supprimer
                        </button>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <div class="result-grid">
                    <!-- 5 CHAMPS GARANTIS (minimum requis) -->
                    <div class="result-field">
                        <span class="result-label">Genre</span>
                        <span class="result-value">${escapeHtml(genre)}</span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Âge</span>
                        <span class="result-value">${escapeHtml(String(age))}${age !== 'Non spécifié' ? ' ans' : ''}</span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Ville</span>
                        <span class="result-value">${escapeHtml(ville)}</span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Profession</span>
                        <span class="result-value">${escapeHtml(profession)}</span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Degré</span>
                        <span class="result-value">${escapeHtml(degre)}</span>
                    </div>
                    <!-- CHAMPS SUPPLÉMENTAIRES (affichés si disponibles) -->
                    <div class="result-field">
                        <span class="result-label">Moyenne cumulative (CGPA)</span>
                        <span class="result-value ${getStatusClass('cgpa', moyenne)}">
                            ${escapeHtml(String(moyenne))} / 10
                        </span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Pression académique</span>
                        <span class="result-value">${escapeHtml(String(pressionAcademique))}/5</span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Satisfaction des études</span>
                        <span class="result-value">${escapeHtml(String(satisfactionEtudes))}/5</span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Durée du sommeil</span>
                        <span class="result-value">${escapeHtml(dureeSommeil)}</span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Habitudes alimentaires</span>
                        <span class="result-value ${getStatusClass('dietaryHabits', habitudesAlimentaires)}">
                            ${escapeHtml(habitudesAlimentaires)}
                        </span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Stress financier</span>
                        <span class="result-value">${escapeHtml(String(stressFinancier))}/5</span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Dépression</span>
                        <span class="result-value ${getStatusClass('depression', depression)}">
                            ${depression === 0 ? 'Non' : 'Oui'}
                        </span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Pensées suicidaires</span>
                        <span class="result-value ${getStatusClass('suicidalThoughts', penseesSuicidaires)}">
                            ${penseesSuicidaires === 'No' ? 'Non' : 'Oui'}
                        </span>
                    </div>
                    <div class="result-field">
                        <span class="result-label">Antécédents familiaux</span>
                        <span class="result-value">${escapeHtml(antecedentsFamiliaux)}</span>
                    </div>
                </div>
            </div>
        `;
        
        // Ajouter la carte au conteneur
        targetContainer.appendChild(card);
    });
}

// ============================================================================
// FONCTION : Échappement HTML (sécurité)
// ============================================================================

/**
 * Échappe les caractères HTML pour éviter les injections XSS.
 * 
 * Cette fonction remplace les caractères spéciaux HTML par leurs équivalents
 * encodés pour la sécurité.
 * 
 * @param {string} text - Le texte à échapper
 * @returns {string} Le texte échappé
 */
function escapeHtml(text) {
    // Création d'un élément div temporaire
    const div = document.createElement('div');
    // Assignation du texte (le navigateur échappe automatiquement)
    div.textContent = text;
    // Récupération du HTML échappé
    return div.innerHTML;
}

// ============================================================================
// GESTION DES ÉVÉNEMENTS
// ============================================================================

// Événement : Saisie dans le champ de recherche
searchInput.addEventListener('input', (e) => {
    // Récupération de la valeur saisie (sans trim pour garder les espaces)
    const query = e.target.value;
    const queryTrimmed = query.trim();
    
    // Si la recherche est vide, cacher l'autocomplétion
    if (queryTrimmed === '') {
        autocompleteList.classList.remove('show');
        return;
    }
    
    // Debounce : attendre 300ms après la dernière frappe avant d'afficher l'autocomplétion
    // NE PAS faire de recherche automatique pendant la saisie
    clearTimeout(autocompleteTimeout);
    autocompleteTimeout = setTimeout(() => {
        // Afficher SEULEMENT l'autocomplétion, PAS les résultats
        fetchAutocomplete(queryTrimmed);
    }, 300);
});

// Événement : Touche pressée dans le champ de recherche
searchInput.addEventListener('keydown', (e) => {
    // Cas a) : Si l'utilisateur ne saisit rien et appuie sur la barre d'espace,
    // les 10 premiers titres doivent s'afficher automatiquement
    if (e.key === ' ' && searchInput.value.trim() === '') {
        e.preventDefault();  // Empêcher l'ajout de l'espace dans l'input
        console.log('Espace pressé (input vide) : affichage automatique des 10 premiers étudiants');
        // Afficher les 10 premiers étudiants automatiquement
        performSearch(' ', true);  // true = avec scroll automatique vers les résultats
        return;
    }
    
    // Si la touche Entrée est pressée
    if (e.key === 'Enter') {
        // Cacher l'autocomplétion
        autocompleteList.classList.remove('show');
        // Lancer la recherche avec la valeur actuelle
        const query = searchInput.value.trim();
        console.log(`⌨️ Entrée pressée avec query: "${query}"`);
        
        if (query === '') {
            performSearch(' ');  // Les 10 premiers si vide
        } else {
            performSearch(query);
        }
    }
    
    // Si la touche Échap est pressée
    if (e.key === 'Escape') {
        // Cacher l'autocomplétion
        autocompleteList.classList.remove('show');
    }
});

// Événement : Clic sur le bouton de recherche
searchButton.addEventListener('click', () => {
    // Lancer la recherche avec la valeur de l'input
    const query = searchInput.value.trim();
    console.log(`Bouton Rechercher cliqué avec query: "${query}"`);
    
    if (query === '') {
        performSearch(' ');  // Les 10 premiers si vide
    } else {
        performSearch(query);
    }
});

// Événement : Clic en dehors de la zone de recherche
// Pour fermer l'autocomplétion quand on clique ailleurs
document.addEventListener('click', (e) => {
    // Si le clic n'est pas dans le conteneur de recherche
    if (!e.target.closest('.search-container')) {
        autocompleteList.classList.remove('show');
    }
});

// ============================================================================
// INITIALISATION
// ============================================================================

/**
 * Fonction d'initialisation exécutée au chargement de la page.
 * 
 * Cette fonction peut être utilisée pour des actions au démarrage,
 * comme charger les 10 premiers documents automatiquement.
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('✓ Application de recherche initialisée');
    console.log('✓ searchInput:', searchInput ? 'Trouvé' : 'NON TROUVÉ');
    console.log('✓ classicResultsContainer:', classicResultsContainer ? 'Trouvé' : 'NON TROUVÉ');
    console.log('✓ vectorResultsContainer:', vectorResultsContainer ? 'Trouvé' : 'NON TROUVÉ');
    console.log('✓ searchButton:', searchButton ? 'Trouvé' : 'NON TROUVÉ');
    
    // Vérifier que tous les éléments sont présents
    if (!searchInput || !classicResultsContainer) {
        console.error('❌ Éléments manquants! Vérifiez les IDs dans le HTML');
        return;
    }
    
    // Gestion du scroll pour le bouton "Retour en haut"
    window.addEventListener('scroll', () => {
        const scrollTop = document.getElementById('scrollToTop');
        if (scrollTop) {
            if (window.pageYOffset > 300) {
                scrollTop.classList.add('show');
            } else {
                scrollTop.classList.remove('show');
            }
        }
        
        // Mise à jour de la navigation active
        updateActiveNav();
    });
    
    console.log('✓ Application prête. Utilisez la navigation latérale.');
    
    // Charger automatiquement les 10 premiers étudiants au démarrage
    console.log('Chargement automatique des 10 premiers étudiants...');
    performSearch(' ', false); // false = pas de scroll automatique au chargement initial
});

// ============================================================================
// FONCTIONS DE NAVIGATION
// ============================================================================

/**
 * Toggle (afficher/cacher) la sidebar.
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainWrapper = document.querySelector('.main-wrapper');
    
    if (sidebar && mainWrapper) {
        sidebar.classList.toggle('closed');
        mainWrapper.classList.toggle('sidebar-closed');
        
        // Sauvegarder l'état dans localStorage
        const isClosed = sidebar.classList.contains('closed');
        localStorage.setItem('sidebarClosed', isClosed);
    }
}

/**
 * Scroll vers une section spécifique.
 * 
 * @param {string} sectionId - ID de la section cible
 */
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        const offsetTop = section.offsetTop - 20; // Petit offset pour l'espacement
        window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
        });
        
        console.log(`📍 Navigation vers : ${sectionId}`);
        
        // Mettre à jour l'état actif dans la sidebar
        document.querySelectorAll('.sidebar-link').forEach(link => {
            link.classList.remove('active');
        });
        const activeLink = document.querySelector(`.sidebar-link[href="#${sectionId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        // Fermer la sidebar sur mobile après clic
        if (window.innerWidth <= 768) {
            const sidebar = document.getElementById('sidebar');
            if (sidebar && sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
            }
        }
    } else {
        console.warn(`Section ${sectionId} non trouvée`);
    }
}

/**
 * Scroll vers le haut de la page.
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

/**
 * Met à jour l'élément de navigation actif selon la position du scroll.
 */
function updateActiveNav() {
    const sections = ['home', 'vector-search', 'classic-search'];
    const menuItems = document.querySelectorAll('.menu-item');
    
    let currentSection = 'home';
    
    // Trouver la section actuellement visible
    sections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            const rect = section.getBoundingClientRect();
            // Si la section est dans le viewport
            if (rect.top <= 150 && rect.bottom >= 150) {
                currentSection = sectionId;
            }
        }
    });
    
    // Mettre à jour les classes active
    menuItems.forEach(item => {
        if (item.dataset.section === currentSection) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// ============================================================================
// FONCTIONS CRUD - Create, Read, Update, Delete
// ============================================================================

/**
 * Modifier un étudiant.
 * Ouvre un modal avec un formulaire pré-rempli pour modifier les informations.
 * 
 * @param {string} studentId - L'ID MongoDB de l'étudiant
 */
async function editStudent(studentId) {
    try {
        // Récupérer les informations de l'étudiant
        const response = await fetch(`/api/student/${studentId}`);
        const data = await response.json();
        
        if (data.success) {
            const student = data.student;
            
            // Créer le formulaire d'édition
            const modalHTML = `
                <div class="modal-overlay" id="editModal">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Modifier l'Étudiant ID: ${student.id}</h2>
                            <button class="modal-close" onclick="closeModal()" title="Fermer">×</button>
                        </div>
                        <form id="editForm" class="edit-form">
                            <input type="hidden" id="edit_id" value="${studentId}">
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Genre</label>
                                    <select id="edit_gender">
                                        <option value="Male" ${student.gender === 'Male' ? 'selected' : ''}>Male</option>
                                        <option value="Female" ${student.gender === 'Female' ? 'selected' : ''}>Female</option>
                                    </select>
                                </div>
                                
                                <div class="form-group">
                                    <label>Âge</label>
                                    <input type="number" id="edit_age" value="${student.age}" min="18" max="100">
                                </div>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Ville</label>
                                    <input type="text" id="edit_city" value="${student.city}">
                                </div>
                                
                                <div class="form-group">
                                    <label>Profession</label>
                                    <input type="text" id="edit_profession" value="${student.profession}">
                                </div>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Degré</label>
                                    <input type="text" id="edit_degree" value="${student.degree}">
                                </div>
                                
                                <div class="form-group">
                                    <label>CGPA</label>
                                    <input type="number" id="edit_cgpa" value="${student.cgpa}" min="0" max="10" step="0.01">
                                </div>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Pression académique (0-5)</label>
                                    <input type="number" id="edit_academicPressure" value="${student.academicPressure}" min="0" max="5">
                                </div>
                                
                                <div class="form-group">
                                    <label>Satisfaction études (0-5)</label>
                                    <input type="number" id="edit_studySatisfaction" value="${student.studySatisfaction}" min="0" max="5">
                                </div>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Durée du sommeil</label>
                                    <select id="edit_sleepDuration">
                                        <option value="Less than 5 hours" ${student.sleepDuration === 'Less than 5 hours' ? 'selected' : ''}>Less than 5 hours</option>
                                        <option value="5-6 hours" ${student.sleepDuration === '5-6 hours' ? 'selected' : ''}>5-6 hours</option>
                                        <option value="7-8 hours" ${student.sleepDuration === '7-8 hours' ? 'selected' : ''}>7-8 hours</option>
                                        <option value="More than 8 hours" ${student.sleepDuration === 'More than 8 hours' ? 'selected' : ''}>More than 8 hours</option>
                                    </select>
                                </div>
                                
                                <div class="form-group">
                                    <label>Habitudes alimentaires</label>
                                    <select id="edit_dietaryHabits">
                                        <option value="Healthy" ${student.dietaryHabits === 'Healthy' ? 'selected' : ''}>Healthy</option>
                                        <option value="Moderate" ${student.dietaryHabits === 'Moderate' ? 'selected' : ''}>Moderate</option>
                                        <option value="Unhealthy" ${student.dietaryHabits === 'Unhealthy' ? 'selected' : ''}>Unhealthy</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Stress financier (0-5)</label>
                                    <input type="number" id="edit_financialStress" value="${student.financialStress}" min="0" max="5">
                                </div>
                                
                                <div class="form-group">
                                    <label>Dépression</label>
                                    <select id="edit_depression">
                                        <option value="0" ${student.depression === 0 ? 'selected' : ''}>Non (0)</option>
                                        <option value="1" ${student.depression === 1 ? 'selected' : ''}>Oui (1)</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Pensées suicidaires</label>
                                    <select id="edit_suicidalThoughts">
                                        <option value="No" ${student.suicidalThoughts === 'No' ? 'selected' : ''}>No</option>
                                        <option value="Yes" ${student.suicidalThoughts === 'Yes' ? 'selected' : ''}>Yes</option>
                                    </select>
                                </div>
                                
                                <div class="form-group">
                                    <label>Antécédents familiaux</label>
                                    <select id="edit_familyHistoryMentalIllness">
                                        <option value="No" ${student.familyHistoryMentalIllness === 'No' ? 'selected' : ''}>No</option>
                                        <option value="Yes" ${student.familyHistoryMentalIllness === 'Yes' ? 'selected' : ''}>Yes</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="modal-actions">
                                <button type="button" class="btn-cancel" onclick="closeModal()">Annuler</button>
                                <button type="submit" class="btn-submit">Mettre à jour</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
            
            // Ajouter le modal au body
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            // Gérer la soumission du formulaire
            document.getElementById('editForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                await updateStudent(studentId);
            });
            
        } else {
            alert('Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur lors de la récupération de l\'étudiant:', error);
        alert('Erreur de connexion au serveur');
    }
}

/**
 * Met à jour l'étudiant avec les nouvelles informations.
 * 
 * @param {string} studentId - L'ID MongoDB de l'étudiant
 */
async function updateStudent(studentId) {
    try {
        // Récupérer les valeurs du formulaire
        const updatedData = {
            gender: document.getElementById('edit_gender').value,
            age: parseInt(document.getElementById('edit_age').value),
            city: document.getElementById('edit_city').value,
            profession: document.getElementById('edit_profession').value,
            degree: document.getElementById('edit_degree').value,
            cgpa: parseFloat(document.getElementById('edit_cgpa').value),
            academicPressure: parseInt(document.getElementById('edit_academicPressure').value),
            studySatisfaction: parseInt(document.getElementById('edit_studySatisfaction').value),
            sleepDuration: document.getElementById('edit_sleepDuration').value,
            dietaryHabits: document.getElementById('edit_dietaryHabits').value,
            financialStress: parseInt(document.getElementById('edit_financialStress').value),
            depression: parseInt(document.getElementById('edit_depression').value),
            suicidalThoughts: document.getElementById('edit_suicidalThoughts').value,
            familyHistoryMentalIllness: document.getElementById('edit_familyHistoryMentalIllness').value
        };
        
        // Envoyer la requête de mise à jour
        const response = await fetch(`/api/student/${studentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            closeModal();
            // Recharger la recherche actuelle pour voir les changements
            performSearch(searchInput.value.trim() || ' ');
        } else {
            alert('Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur lors de la mise à jour:', error);
        alert('Erreur de connexion au serveur');
    }
}

/**
 * Supprime un étudiant après confirmation.
 * 
 * @param {string} studentId - L'ID MongoDB de l'étudiant
 * @param {number} studentDisplayId - L'ID d'affichage de l'étudiant
 */
async function deleteStudent(studentId, studentDisplayId) {
    // Demander confirmation
    if (!confirm(`Êtes-vous sûr de vouloir supprimer l'étudiant ID ${studentDisplayId} ?\n\nCette action est irréversible !`)) {
        return;
    }
    
    try {
        // Envoyer la requête de suppression
        const response = await fetch(`/api/student/${studentId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            // Recharger la recherche actuelle
            performSearch(searchInput.value.trim() || ' ');
        } else {
            alert('Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur lors de la suppression:', error);
        alert('Erreur de connexion au serveur');
    }
}

/**
 * Ferme le modal d'édition ou de création.
 */
function closeModal() {
    const editModal = document.getElementById('editModal');
    const createModal = document.getElementById('createModal');
    
    if (editModal) {
        editModal.remove();
    }
    if (createModal) {
        createModal.remove();
    }
}

/**
 * Effectue une recherche vectorielle ML avec post-traitement.
 * Cette fonction utilise Sentence Transformers + 3 modèles ML.
 * Scroll automatiquement vers les résultats.
 */
async function performVectorSearch() {
    try {
        // Récupérer la requête
        const query = vectorSearchInput.value.trim();
        
        if (!query) {
            alert('Veuillez entrer une description de recherche.');
            return;
        }
        
        // Scroll immédiatement vers la section de recherche vectorielle
        scrollToSection('vector-search');
        
        // Afficher le message de chargement
        if (vectorLoadingMessage) vectorLoadingMessage.style.display = 'block';
        if (vectorResultsContainer) vectorResultsContainer.innerHTML = '';
        
        // Désactiver le bouton pendant la recherche
        vectorSearchButton.disabled = true;
        vectorSearchButton.style.opacity = '0.6';
        vectorSearchButton.textContent = 'Traitement en cours...';
        
        // Appel à l'API de recherche vectorielle ML
        const response = await fetch('/api/vector-search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                top_k: 10
            })
        });
        
        const data = await response.json();
        
        // Réactiver le bouton
        vectorSearchButton.disabled = false;
        vectorSearchButton.style.opacity = '1';
        vectorSearchButton.textContent = '🔍 Recherche Vectorielle ML';
        
        // Cacher le message de chargement
        if (vectorLoadingMessage) vectorLoadingMessage.style.display = 'none';
        
        if (data.success) {
            // Debug: afficher les visualisations reçues
            console.log('📊 Visualisations reçues:', data.visualizations);
            
            // Afficher l'en-tête avec informations sur la recherche
            const headerDiv = document.createElement('div');
            headerDiv.className = 'similar-header';
            
            // Construire les liens de visualisation
            let vizLinksHtml = '';
            let vizImagesHtml = '';
            
            if (data.visualizations && data.visualizations.length > 0) {
                const labels = ['Random Forest (Classification)', 'Régression Linéaire (Pertinence)', 'K-Means (Clustering)'];
                
                // Liens cliquables
                vizLinksHtml = data.visualizations.map((vizUrl, index) => {
                    return `<a href="${vizUrl}" target="_blank" class="viz-link" style="display: inline-block; padding: 12px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: bold; transition: transform 0.2s; margin: 5px;">
                        ${labels[index] || `Graphique ${index + 1}`}
                    </a>`;
                }).join('');
                
                // Images directement affichées
                vizImagesHtml = '<div style="margin-top: 30px; text-align: center;"><h3 style="color: #667eea; margin-bottom: 15px;">Visualisations ML</h3><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">' +
                    data.visualizations.map(vizUrl => {
                        return `<div style="background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <img src="${vizUrl}" alt="Visualisation ML" style="width: 100%; height: auto; border-radius: 5px; cursor: pointer;" onerror="this.style.display='none'; console.error('Erreur chargement image:', '${vizUrl}');" onload="console.log('Image chargée:', '${vizUrl}');" onclick="window.open('${vizUrl}', '_blank')">
                        </div>`;
                    }).join('') +
                    '</div></div>';
            } else {
                vizLinksHtml = '<p style="color: #999; font-style: italic;">Visualisations en cours de génération...</p>';
            }
            
            headerDiv.innerHTML = `
                <h2 style="color: #667eea; text-align: center; margin-bottom: 15px;">
                    Résultats de la Recherche Vectorielle ML
                </h2>
                <p style="text-align: center; color: #666; margin-bottom: 20px; font-size: 1.1em;">
                    Requête : "${query}"
                </p>
                <p style="text-align: center; color: #666; margin-bottom: 20px;">
                    ${data.count} étudiants trouvés avec post-traitement par 3 modèles ML :
                    <br>
                    <strong>Random Forest</strong> (classification), <strong>Linear Regression</strong> (prédiction), <strong>K-Means</strong> (clustering)
                </p>
                <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; margin-top: 20px;">
                    ${vizLinksHtml}
                </div>
                ${vizImagesHtml}
            `;
            if (vectorResultsContainer) vectorResultsContainer.appendChild(headerDiv);
            
            // Afficher les résultats avec tous les scores ML
            data.results.forEach((student, index) => {
                displayMLResult(student, index + 1, vectorResultsContainer);
            });
            
        } else {
            if (vectorResultsContainer) {
                vectorResultsContainer.innerHTML = `
                    <div class="error-message" style="text-align: center; padding: 40px; color: #dc3545;">
                        <h3>Erreur</h3>
                        <p>${data.error}</p>
                        ${!data.error.includes('disponible') ? '' : '<p style="margin-top: 15px;"><small>Pour activer la recherche ML, installez : <code>pip install -r requirements_ml.txt</code></small></p>'}
                    </div>
                `;
            }
        }
        
    } catch (error) {
        if (vectorLoadingMessage) vectorLoadingMessage.style.display = 'none';
        vectorSearchButton.disabled = false;
        vectorSearchButton.style.opacity = '1';
        vectorSearchButton.textContent = '🔍 Recherche Vectorielle ML';
        
        console.error('Erreur lors de la recherche vectorielle ML:', error);
        if (vectorResultsContainer) {
            vectorResultsContainer.innerHTML = `
                <div class="error-message" style="text-align: center; padding: 40px; color: #dc3545;">
                    <h3>❌ Erreur de Connexion</h3>
                    <p>Impossible de se connecter au serveur.</p>
                </div>
            `;
        }
    }
}

/**
 * Affiche un résultat de recherche ML avec tous les scores.
 * Garantit l'affichage d'au moins 5 champs de base pour chaque document.
 * 
 * @param {Object} student - L'étudiant à afficher
 * @param {number} rank - Le rang du résultat
 * @param {HTMLElement} container - Conteneur où afficher (optionnel, défaut: vectorResultsContainer)
 */
function displayMLResult(student, rank, container = null) {
    // Utiliser le conteneur fourni ou le conteneur vectoriel par défaut
    const targetContainer = container || vectorResultsContainer;
    
    if (!targetContainer) {
        console.error('Conteneur de résultats vectoriels non trouvé');
        return;
    }
    const card = document.createElement('div');
    card.className = 'result-card ml-result-card';
    
    // Fonction helper pour obtenir une valeur propre
    const getValue = (val, defaultVal = 'Non spécifié') => {
        if (val === null || val === undefined || val === '') return defaultVal;
        return String(val).trim();
    };
    
    // Déterminer les couleurs selon les scores
    const similarityPercent = (student.similarity * 100).toFixed(1);
    const relevanceScore = (student.relevance_score || 0.5) * 100;
    const relevancePercent = relevanceScore.toFixed(1);
    const categoryConfidence = ((student.category_confidence || 0.5) * 100).toFixed(1);
    
    // Couleur du badge de similarité
    let simColor = '#28a745';
    if (similarityPercent < 70) simColor = '#ffc107';
    if (similarityPercent < 50) simColor = '#dc3545';
    
    // Couleur du score de pertinence
    let relevanceColor = '#10b981';
    if (relevanceScore < 40) relevanceColor = '#ef4444';
    else if (relevanceScore < 70) relevanceColor = '#f59e0b';
    
    // Extraire les valeurs avec gestion des valeurs manquantes
    // Au moins 5 champs garantis :
    const id = getValue(student.id || student.data?.id, 'N/A');
    const gender = getValue(student.gender || student.data?.gender, 'Non spécifié');
    const age = getValue(student.age || student.data?.age, 'Non spécifié');
    const city = getValue(student.city || student.data?.city, 'Non spécifié');
    const profession = getValue(student.profession || student.data?.profession, 'Non spécifié');
    const degree = getValue(student.degree || student.data?.degree, 'Non spécifié');
    const cgpa = getValue(student.cgpa || student.data?.cgpa, 'N/A');
    const academicPressure = getValue(student.academicPressure || student.data?.academicPressure, 'N/A');
    const studySatisfaction = getValue(student.studySatisfaction || student.data?.studySatisfaction, 'N/A');
    const financialStress = getValue(student.financialStress || student.data?.financialStress, 'N/A');
    const depression = student.depression !== undefined ? student.depression : (student.data?.depression !== undefined ? student.data.depression : null);
    const sleepDuration = getValue(student.sleepDuration || student.data?.sleepDuration, 'Non spécifié');
    const dietaryHabits = getValue(student.dietaryHabits || student.data?.dietaryHabits, 'Non spécifié');
    
    card.innerHTML = `
        <div class="card-header">
            <div class="card-header-content">
                <h3 class="student-id">Étudiant ID: ${escapeHtml(String(id))}</h3>
                <div class="ml-scores">
                    <span class="ml-badge" style="background: ${simColor};">
                        Similarité: ${similarityPercent}%
                    </span>
                    <span class="ml-badge" style="background: ${relevanceColor};">
                        Pertinence: ${relevancePercent}%
                    </span>
                    <span class="ml-badge" style="background: #8b5cf6;">
                        Cluster: ${student.cluster || 0}
                    </span>
                </div>
            </div>
        </div>
        <div class="card-body">
            <div class="result-grid">
                <!-- Au moins 5 champs garantis -->
                <div class="result-field">
                    <span class="result-label">Genre</span>
                    <span class="result-value">${escapeHtml(gender)}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">Âge</span>
                    <span class="result-value">${escapeHtml(String(age))}${age !== 'Non spécifié' ? ' ans' : ''}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">Ville</span>
                    <span class="result-value">${escapeHtml(city)}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">Profession</span>
                    <span class="result-value">${escapeHtml(profession)}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">Degré</span>
                    <span class="result-value">${escapeHtml(degree)}</span>
                </div>
                <!-- Champs supplémentaires -->
                <div class="result-field">
                    <span class="result-label">CGPA</span>
                    <span class="result-value">${escapeHtml(String(cgpa))}${cgpa !== 'N/A' ? ' / 10' : ''}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">Pression académique</span>
                    <span class="result-value">${escapeHtml(String(academicPressure))}${academicPressure !== 'N/A' ? '/5' : ''}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">Satisfaction des études</span>
                    <span class="result-value">${escapeHtml(String(studySatisfaction))}${studySatisfaction !== 'N/A' ? '/5' : ''}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">Stress financier</span>
                    <span class="result-value">${escapeHtml(String(financialStress))}${financialStress !== 'N/A' ? '/5' : ''}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">Durée du sommeil</span>
                    <span class="result-value">${escapeHtml(sleepDuration)}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">Habitudes alimentaires</span>
                    <span class="result-value">${escapeHtml(dietaryHabits)}</span>
                </div>
                <div class="result-field">
                    <span class="result-label">Dépression (Réel)</span>
                    <span class="result-value">${depression !== null ? (depression === 0 || depression === '0' ? 'Non' : 'Oui') : 'Non spécifié'}</span>
                </div>
                <!-- Scores ML des trois algorithmes -->
                <div class="result-field ml-prediction" style="background: #f0f9ff; padding: 10px; border-radius: 5px; margin-top: 10px;">
                    <span class="result-label" style="font-weight: bold; color: #667eea;">Random Forest (Classification)</span>
                    <span class="result-value" style="font-weight: bold; color: #667eea;">
                        ${student.predicted_category || 'Unknown'} (Confiance: ${categoryConfidence}%)
                    </span>
                </div>
                <div class="result-field ml-prediction" style="background: #fef3c7; padding: 10px; border-radius: 5px;">
                    <span class="result-label" style="font-weight: bold; color: #f59e0b;">Régression Linéaire (Pertinence)</span>
                    <span class="result-value" style="font-weight: bold; color: ${relevanceColor};">
                        ${relevancePercent}% (Score: ${(student.relevance_score || 0.5).toFixed(3)})
                    </span>
                </div>
                <div class="result-field ml-prediction" style="background: #f3e8ff; padding: 10px; border-radius: 5px;">
                    <span class="result-label" style="font-weight: bold; color: #8b5cf6;">K-Means (Cluster)</span>
                    <span class="result-value" style="font-weight: bold; color: #8b5cf6;">
                        Cluster ${student.cluster || 0}
                    </span>
                </div>
            </div>
        </div>
    `;
    
    targetContainer.appendChild(card);
}

/**
 * Trouve des étudiants similaires à un étudiant donné.
 * Utilise la recherche vectorielle simple (sans ML).
 * 
 * @param {string} studentId - L'ID MongoDB de l'étudiant de référence
 * @param {number} displayId - L'ID d'affichage de l'étudiant
 */
async function findSimilarStudents(studentId, displayId) {
    try {
        // Scroll vers la section de recherche classique pour afficher les résultats similaires
        scrollToSection('classic-search');
        
        // Afficher le message de chargement
        if (loadingMessage) loadingMessage.style.display = 'block';
        if (classicResultsContainer) classicResultsContainer.innerHTML = '';
        
        // Appel à l'API de recherche vectorielle
        const response = await fetch(`/api/similar/${studentId}`);
        const data = await response.json();
        
        // Cacher le message de chargement
        if (loadingMessage) loadingMessage.style.display = 'none';
        
        if (data.success) {
            // Afficher un en-tête explicatif
            const headerDiv = document.createElement('div');
            headerDiv.className = 'similar-header';
            headerDiv.innerHTML = `
                <h2 style="color: #667eea; text-align: center; margin-bottom: 15px;">
                    Étudiants Similaires à l'Étudiant ID ${displayId}
                </h2>
                <p style="text-align: center; color: #666; margin-bottom: 30px; font-size: 1.1em;">
                    Affichage des ${data.count} étudiants les plus similaires basé sur leur profil
                    <br>
                    <small style="color: #999;">
                        (Similarité calculée sur : âge, stress, dépression, performance académique, etc.)
                    </small>
                </p>
            `;
            if (classicResultsContainer) classicResultsContainer.appendChild(headerDiv);
            
            // Afficher les étudiants similaires avec leur score
            data.similar_students.forEach((student, index) => {
                // Calcul du pourcentage de similarité
                const similarity_percent = (student.similarity_score * 100).toFixed(1);
                
                // Déterminer la couleur selon le score
                let scoreColor = '#28a745'; // Vert pour haute similarité
                if (similarity_percent < 70) scoreColor = '#ffc107'; // Jaune pour moyenne
                if (similarity_percent < 50) scoreColor = '#dc3545'; // Rouge pour faible
                
                // Créer la carte comme d'habitude mais avec badge de similarité
                const card = document.createElement('div');
                card.className = 'result-card';
                
                // Utiliser la même fonction d'affichage mais ajouter le score
                const cleanValue = (val) => {
                    if (val === null || val === undefined) return 'Non spécifié';
                    const str = String(val).trim();
                    return str.replace(/^["']|["']$/g, '');
                };
                
                const id = student.id || 'N/A';
                const genre = cleanValue(student.gender);
                const age = student.age || 'Non spécifié';
                const ville = cleanValue(student.city);
                const profession = cleanValue(student.profession);
                const degre = cleanValue(student.degree);
                const moyenne = student.cgpa || 'N/A';
                const pressionAcademique = student.academicPressure || 'N/A';
                const satisfactionEtudes = student.studySatisfaction || 'N/A';
                const stressFinancier = student.financialStress || 'N/A';
                const depression = student.depression || 'N/A';
                
                card.innerHTML = `
                    <div class="card-header">
                        <div class="card-header-content">
                            <h3 class="student-id">Étudiant ID: ${escapeHtml(String(id))}</h3>
                            <div class="similarity-badge" style="background: ${scoreColor}; color: white; padding: 8px 15px; border-radius: 20px; font-weight: bold;">
                                Similarité : ${similarity_percent}%
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="result-grid">
                            <div class="result-field">
                                <span class="result-label">Genre</span>
                                <span class="result-value">${escapeHtml(genre)}</span>
                            </div>
                            <div class="result-field">
                                <span class="result-label">Âge</span>
                                <span class="result-value">${escapeHtml(String(age))} ans</span>
                            </div>
                            <div class="result-field">
                                <span class="result-label">Ville</span>
                                <span class="result-value">${escapeHtml(ville)}</span>
                            </div>
                            <div class="result-field">
                                <span class="result-label">Profession</span>
                                <span class="result-value">${escapeHtml(profession)}</span>
                            </div>
                            <div class="result-field">
                                <span class="result-label">Degré</span>
                                <span class="result-value">${escapeHtml(degre)}</span>
                            </div>
                            <div class="result-field">
                                <span class="result-label">Moyenne cumulative (CGPA)</span>
                                <span class="result-value">${escapeHtml(String(moyenne))} / 10</span>
                            </div>
                            <div class="result-field">
                                <span class="result-label">Pression académique</span>
                                <span class="result-value">${escapeHtml(String(pressionAcademique))}/5</span>
                            </div>
                            <div class="result-field">
                                <span class="result-label">Stress financier</span>
                                <span class="result-value">${escapeHtml(String(stressFinancier))}/5</span>
                            </div>
                            <div class="result-field">
                                <span class="result-label">Dépression</span>
                                <span class="result-value">${depression === 0 ? 'Non' : 'Oui'}</span>
                            </div>
                        </div>
                    </div>
                `;
                
                if (classicResultsContainer) classicResultsContainer.appendChild(card);
            });
            
        } else {
            if (classicResultsContainer) {
                classicResultsContainer.innerHTML = `
                    <div class="error-message" style="text-align: center; padding: 40px; color: #dc3545;">
                        <h3>Erreur</h3>
                        <p>${data.error || 'Impossible de trouver des étudiants similaires'}</p>
                    </div>
                `;
            }
        }
        
    } catch (error) {
        if (loadingMessage) loadingMessage.style.display = 'none';
        console.error('Erreur lors de la recherche de similarité:', error);
        if (classicResultsContainer) {
            classicResultsContainer.innerHTML = `
                <div class="error-message" style="text-align: center; padding: 40px; color: #dc3545;">
                    <h3>❌ Erreur de Connexion</h3>
                    <p>Impossible de se connecter au serveur.</p>
                </div>
            `;
        }
    }
}

/**
 * Ouvre le formulaire de création d'un nouvel étudiant.
 * Affiche un modal avec un formulaire vierge.
 */
function createNewStudent() {
    // Créer le formulaire de création (champs vides)
    const modalHTML = `
        <div class="modal-overlay" id="createModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Créer un Nouvel Étudiant</h2>
                    <button class="modal-close" onclick="closeModal()" title="Fermer">×</button>
                </div>
                <form id="createForm" class="edit-form">
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>ID de l'étudiant (unique)</label>
                            <input type="number" id="create_id" placeholder="Ex: 25000" required min="1">
                        </div>
                        
                        <div class="form-group">
                            <label>Genre</label>
                            <select id="create_gender" required>
                                <option value="">-- Sélectionnez --</option>
                                <option value="Male">Male</option>
                                <option value="Female">Female</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Âge</label>
                            <input type="number" id="create_age" placeholder="Ex: 25" required min="18" max="100">
                        </div>
                        
                        <div class="form-group">
                            <label>Ville</label>
                            <input type="text" id="create_city" placeholder="Ex: Mumbai" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Profession</label>
                            <input type="text" id="create_profession" placeholder="Ex: Student" required>
                        </div>
                        
                        <div class="form-group">
                            <label>Degré</label>
                            <input type="text" id="create_degree" placeholder="Ex: MBA" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>CGPA (Moyenne cumulative)</label>
                            <input type="number" id="create_cgpa" placeholder="Ex: 7.5" required min="0" max="10" step="0.01">
                        </div>
                        
                        <div class="form-group">
                            <label>Pression académique (0-5)</label>
                            <input type="number" id="create_academicPressure" placeholder="0 à 5" required min="0" max="5" value="3">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Satisfaction des études (0-5)</label>
                            <input type="number" id="create_studySatisfaction" placeholder="0 à 5" required min="0" max="5" value="3">
                        </div>
                        
                        <div class="form-group">
                            <label>Stress financier (0-5)</label>
                            <input type="number" id="create_financialStress" placeholder="0 à 5" required min="0" max="5" value="2">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Durée du sommeil</label>
                            <select id="create_sleepDuration" required>
                                <option value="">-- Sélectionnez --</option>
                                <option value="Less than 5 hours">Less than 5 hours</option>
                                <option value="5-6 hours" selected>5-6 hours</option>
                                <option value="7-8 hours">7-8 hours</option>
                                <option value="More than 8 hours">More than 8 hours</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Habitudes alimentaires</label>
                            <select id="create_dietaryHabits" required>
                                <option value="">-- Sélectionnez --</option>
                                <option value="Healthy" selected>Healthy</option>
                                <option value="Moderate">Moderate</option>
                                <option value="Unhealthy">Unhealthy</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Dépression</label>
                            <select id="create_depression" required>
                                <option value="0" selected>Non (0)</option>
                                <option value="1">Oui (1)</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Pensées suicidaires</label>
                            <select id="create_suicidalThoughts" required>
                                <option value="No" selected>No</option>
                                <option value="Yes">Yes</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Antécédents familiaux</label>
                            <select id="create_familyHistoryMentalIllness" required>
                                <option value="No" selected>No</option>
                                <option value="Yes">Yes</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Satisfaction au travail (0-5)</label>
                            <input type="number" id="create_jobSatisfaction" placeholder="0 à 5" value="0" min="0" max="5">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Pression au travail (0-5)</label>
                            <input type="number" id="create_workPressure" placeholder="0 à 5" value="0" min="0" max="5">
                        </div>
                        
                        <div class="form-group">
                            <label>Heures de travail/études par jour</label>
                            <input type="number" id="create_studyHours" placeholder="Ex: 8" value="8" min="0" max="24">
                        </div>
                    </div>
                    
                    <div class="modal-actions">
                        <button type="button" class="btn-cancel" onclick="closeModal()">Annuler</button>
                        <button type="submit" class="btn-submit">Créer l'Étudiant</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    // Ajouter le modal au body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Gérer la soumission du formulaire
    document.getElementById('createForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveNewStudent();
    });
}

/**
 * Sauvegarde le nouvel étudiant dans MongoDB.
 */
async function saveNewStudent() {
    try {
        // Récupérer les valeurs du formulaire
        const newStudentData = {
            id: parseInt(document.getElementById('create_id').value),
            gender: document.getElementById('create_gender').value,
            age: parseInt(document.getElementById('create_age').value),
            city: document.getElementById('create_city').value,
            profession: document.getElementById('create_profession').value,
            degree: document.getElementById('create_degree').value,
            cgpa: parseFloat(document.getElementById('create_cgpa').value),
            academicPressure: parseInt(document.getElementById('create_academicPressure').value),
            studySatisfaction: parseInt(document.getElementById('create_studySatisfaction').value),
            sleepDuration: document.getElementById('create_sleepDuration').value,
            dietaryHabits: document.getElementById('create_dietaryHabits').value,
            financialStress: parseInt(document.getElementById('create_financialStress').value),
            depression: parseInt(document.getElementById('create_depression').value),
            suicidalThoughts: document.getElementById('create_suicidalThoughts').value,
            familyHistoryMentalIllness: document.getElementById('create_familyHistoryMentalIllness').value,
            jobSatisfaction: parseInt(document.getElementById('create_jobSatisfaction').value),
            workPressure: parseInt(document.getElementById('create_workPressure').value),
            studyHours: parseInt(document.getElementById('create_studyHours').value)
        };
        
        // Vérifier que l'ID n'existe pas déjà
        const checkResponse = await fetch(`/api/search?query=id:${newStudentData.id}`);
        const checkData = await checkResponse.json();
        
        if (checkData.results && checkData.results.length > 0) {
            alert(`Erreur: Un étudiant avec l'ID ${newStudentData.id} existe déjà!\nVeuillez choisir un autre ID.`);
            return;
        }
        
        // Envoyer la requête de création
        const response = await fetch('/api/student', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newStudentData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message + '\n\nÉtudiant ID: ' + newStudentData.id);
            closeModal();
            // Rechercher le nouvel étudiant pour l'afficher
            searchInput.value = `id:${newStudentData.id}`;
            performSearch(`id:${newStudentData.id}`);
        } else {
            alert('Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur lors de la création:', error);
        alert('Erreur de connexion au serveur');
    }
}

