#!/usr/bin/env python3
"""
Generuje diagram klas UML dla Extended Spotify App
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

# Konfiguracja wykresu
fig, ax = plt.subplots(figsize=(20, 14))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Kolory
COLOR_MODEL = '#E8F4F8'
COLOR_VIEW = '#FFF4E6'
COLOR_SERVICE = '#F0F8E8'
COLOR_STORE = '#F8E8F8'

def draw_class(ax, x, y, width, height, class_name, attributes, methods, color):
    """Rysuje klasę UML"""
    # Ramka klasy
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.1",
        edgecolor='black',
        facecolor=color,
        linewidth=2
    )
    ax.add_patch(box)
    
    # Nazwa klasy (pogrubiona)
    ax.text(x + width/2, y + height - 1.5, class_name,
            ha='center', va='top', fontsize=9, fontweight='bold')
    
    # Linia oddzielająca nazwę
    ax.plot([x, x + width], [y + height - 3, y + height - 3], 'k-', linewidth=1)
    
    # Atrybuty
    attr_y = y + height - 4
    for attr in attributes:
        # Skróć tekst jeśli za długi - oblicz max chars na podstawie szerokości
        max_chars = int(width * 2.2)  # Dynamicznie na podstawie szerokości boxu
        display_attr = attr[:max_chars] + '...' if len(attr) > max_chars else attr
        ax.text(x + 0.5, attr_y, display_attr, ha='left', va='top', 
                fontsize=6.5, family='monospace', clip_on=True)
        attr_y -= 1.0
    
    # Linia oddzielająca atrybuty i metody
    if methods:
        ax.plot([x, x + width], [attr_y + 0.3, attr_y + 0.3], 'k-', linewidth=1)
        attr_y -= 0.8
    
    # Metody
    for method in methods:
        # Skróć tekst jeśli za długi - oblicz max chars na podstawie szerokości
        max_chars = int(width * 2.2)  # Dynamicznie na podstawie szerokości boxu
        display_method = method[:max_chars] + '...' if len(method) > max_chars else method
        ax.text(x + 0.5, attr_y, display_method, ha='left', va='top', 
                fontsize=6.5, family='monospace', clip_on=True)
        attr_y -= 1.0

def draw_arrow(ax, x1, y1, x2, y2, style='solid', label=''):
    """Rysuje strzałkę między klasami"""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='->' if style == 'solid' else '-|>',
        connectionstyle='arc3,rad=0.1',
        linewidth=1.5,
        color='black',
        linestyle='-' if style == 'solid' else '--'
    )
    ax.add_patch(arrow)
    
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y + 1, label, ha='center', va='bottom', 
                fontsize=7, style='italic', bbox=dict(boxstyle='round,pad=0.3', 
                facecolor='white', edgecolor='none'))

# BACKEND MODELS

# User (Django built-in)
draw_class(ax, 5, 74, 20, 16, '«model»\nUser',
    [
        '- id: Integer',
        '- username: String',
        '- email: String',
        '- password: String',
        '- spotify_access_token: String',
        '- spotify_refresh_token: String',
        '- spotify_token_expires: DateTime',
        '- spotify_user_id: String'
    ],
    [
        '+ authenticate()',
        '+ save()',
        '+ delete()'
    ],
    COLOR_MODEL)

# SpotifyDataUpload
draw_class(ax, 30, 74, 20, 16, '«model»\nSpotifyDataUpload',
    [
        '- id: Integer',
        '- user: FK(User)',
        '- file_path: String',
        '- file_size: BigInteger',
        '- upload_date: DateTime',
        '- processed: Boolean',
        '- processing_status: String'
    ],
    [
        '+ save()',
        '+ delete()',
        '+ __str__()'
    ],
    COLOR_MODEL)

# StreamingHistory
draw_class(ax, 55, 73, 24, 20, '«model»\nStreamingHistory',
    [
        '- id: Integer',
        '- user: FK(User)',
        '- upload: FK(SpotifyDataUpload)',
        '- ts: DateTime',
        '- username: String',
        '- platform: String',
        '- ms_played: Integer',
        '- conn_country: String',
        '- track_name: String',
        '- artist_name: String',
        '- album_name: String',
        '- track_uri: String'
    ],
    [
        '+ save()',
        '+ delete()'
    ],
    COLOR_MODEL)

# BACKEND VIEWS/CONTROLLERS

# AuthenticationView
draw_class(ax, 5, 52, 20, 12, '«controller»\nAuthenticationView',
    [],
    [
        '+ register(req)',
        '+ login_view(req)',
        '+ logout_view(req)',
        '+ current_user(req)',
        '+ spotify_login(req)',
        '+ spotify_callback(req)'
    ],
    COLOR_VIEW)

# DataUploadView
draw_class(ax, 30, 47, 26, 18, '«controller»\nDataUploadView',
    [],
    [
        '+ upload_data(req)',
        '+ get_uploads(req)',
        '+ get_stats(req)',
        '+ get_top_tracks(req)',
        '+ gen_playlist(req)',
        '+ get_monthly_stats(req)',
        '+ delete_all_data(req)',
        '- process_zip()',
        '- process_history()'
    ],
    COLOR_VIEW)

# BACKEND SERIALIZERS

# UserSerializer
draw_class(ax, 55, 52, 16, 8, '«serializer»\nUserSerializer',
    [
        '- model: User',
        '- fields: List'
    ],
    [
        '+ to_representation()',
        '+ validate()'
    ],
    COLOR_SERVICE)

# SpotifyDataUploadSerializer
draw_class(ax, 73, 52, 21, 9, '«serializer»\nUploadSerializer',
    [
        '- model: Upload',
        '- fields: List',
        '- read_only: List'
    ],
    [
        '+ to_representation()',
        '+ validate()'
    ],
    COLOR_SERVICE)

# FRONTEND STORES

# AuthStore
draw_class(ax, 5, 32, 20, 12, '«store»\nAuthStore',
    [
        '- user: ref(null)',
        '- isAuthenticated: ref',
        '- loading: ref(false)',
        '- error: ref(null)'
    ],
    [
        '+ login(user, pass)',
        '+ register(...)',
        '+ logout()',
        '+ checkAuth()',
        '+ spotifyLogin()'
    ],
    COLOR_STORE)

# FRONTEND SERVICES

# authService
draw_class(ax, 30, 32, 17, 10, '«service»\nauthService',
    [],
    [
        '+ register(...)',
        '+ login(user, pass)',
        '+ logout()',
        '+ getCurrentUser()',
        '+ spotifyLogin()',
        '+ spotifyCallback()'
    ],
    COLOR_SERVICE)

# uploadService
draw_class(ax, 50, 31, 19, 13, '«service»\nuploadService',
    [],
    [
        '+ uploadFile(file)',
        '+ getUploads()',
        '+ getStats()',
        '+ getTopTracks(p)',
        '+ genPlaylist(p)',
        '+ getMonthlyStats()',
        '+ deleteAllData()'
    ],
    COLOR_SERVICE)

# spotifyService
draw_class(ax, 72, 32, 17, 8, '«service»\nspotifyService',
    [],
    [
        '+ getAuthUrl()',
        '+ getPlaylists()',
        '+ createPlaylist(...)',
        '+ addTracks(...)'
    ],
    COLOR_SERVICE)

# FRONTEND VIEWS/COMPONENTS

# Dashboard
draw_class(ax, 5, 14, 13, 8, '«view»\nDashboard',
    [
        '- stats: ref({})',
        '- uploads: ref([])'
    ],
    [
        '+ loadStats()',
        '+ deleteAllData()'
    ],
    COLOR_VIEW)

# TopTracks
draw_class(ax, 21, 14, 13, 8, '«view»\nTopTracks',
    [
        '- tracks: ref([])',
        '- startDate: ref("")',
        '- endDate: ref("")'
    ],
    [
        '+ loadTopTracks()',
        '+ filterByDate()'
    ],
    COLOR_VIEW)

# GeneratePlaylist
draw_class(ax, 37, 14, 15, 8, '«view»\nGeneratePlaylist',
    [
        '- tracks: ref([])',
        '- limit: ref(50)',
        '- dates: ref({})'
    ],
    [
        '+ genPlaylist()',
        '+ createSpotify()'
    ],
    COLOR_VIEW)

# Charts
draw_class(ax, 54, 14, 12, 8, '«view»\nCharts',
    [
        '- chartData: ref([])',
        '- chart: null'
    ],
    [
        '+ loadMonthlyStats()',
        '+ createChart()',
        '+ destroyChart()'
    ],
    COLOR_VIEW)

# Upload
draw_class(ax, 69, 14, 11, 7, '«view»\nUpload',
    [
        '- file: ref(null)',
        '- uploading: ref(false)'
    ],
    [
        '+ handleUpload()',
        '+ selectFile()'
    ],
    COLOR_VIEW)

# RELACJE MIĘDZY KLASAMI

# User -> SpotifyDataUpload (1:N)
draw_arrow(ax, 25, 82, 30, 82, 'solid', '1:N')

# User -> StreamingHistory (1:N)
draw_arrow(ax, 25, 80, 55, 85, 'solid', '1:N')

# SpotifyDataUpload -> StreamingHistory (1:N)
draw_arrow(ax, 50, 82, 55, 82, 'solid', '1:N')

# AuthenticationView -> User
draw_arrow(ax, 15, 64, 15, 74, 'solid', 'uses')

# DataUploadView -> SpotifyDataUpload
draw_arrow(ax, 43, 65, 40, 74, 'solid', 'uses')

# DataUploadView -> StreamingHistory
draw_arrow(ax, 56, 60, 67, 73, 'solid', 'uses')

# UserSerializer -> User
draw_arrow(ax, 55, 56, 25, 78, 'solid', 'serializes')

# SpotifyDataUploadSerializer -> SpotifyDataUpload
draw_arrow(ax, 83, 61, 48, 76, 'solid', 'serializes')

# AuthStore -> authService
draw_arrow(ax, 25, 38, 30, 38, 'solid', 'uses')

# authService -> API (represented by connection)
draw_arrow(ax, 38.5, 32, 38.5, 47, 'dashed', 'HTTP')

# uploadService -> API
draw_arrow(ax, 59, 31, 50, 47, 'dashed', 'HTTP')

# spotifyService -> API
draw_arrow(ax, 80, 32, 56, 50, 'dashed', 'HTTP')

# Views -> Stores
draw_arrow(ax, 11, 22, 11, 32, 'solid', 'uses')

# Views -> Services
draw_arrow(ax, 25, 18, 38, 32, 'solid', 'uses')
draw_arrow(ax, 45, 18, 59, 31, 'solid', 'uses')

# TYTUŁ I LEGENDA
ax.text(50, 96, 'Extended Spotify App - Diagram Klas UML', 
        ha='center', fontsize=18, fontweight='bold')

ax.text(50, 93, 'Architektura: Django REST Framework (Backend) + Vue 3 (Frontend)', 
        ha='center', fontsize=11, style='italic')

# Legenda
legend_elements = [
    mpatches.Patch(facecolor=COLOR_MODEL, edgecolor='black', label='Model (Django ORM)'),
    mpatches.Patch(facecolor=COLOR_VIEW, edgecolor='black', label='View/Controller'),
    mpatches.Patch(facecolor=COLOR_SERVICE, edgecolor='black', label='Service/Serializer'),
    mpatches.Patch(facecolor=COLOR_STORE, edgecolor='black', label='Store (Pinia)'),
    mlines.Line2D([], [], color='black', linestyle='-', linewidth=1.5, label='Relacja/Użycie'),
    mlines.Line2D([], [], color='black', linestyle='--', linewidth=1.5, label='HTTP API Call')
]

ax.legend(handles=legend_elements, loc='lower center', ncol=6, 
         frameon=True, fontsize=9, bbox_to_anchor=(0.5, 0.02))

# Adnotacje
ax.text(2, 5, 'Backend Layer', fontsize=10, fontweight='bold', 
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray'))
ax.text(2, 3, '(Django + PostgreSQL)', fontsize=8, style='italic')

ax.text(50, 5, 'Frontend Layer', fontsize=10, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray'))
ax.text(50, 3, '(Vue 3 + Vite)', fontsize=8, style='italic')

# Separator Backend/Frontend
ax.axhline(y=45, color='red', linestyle='--', linewidth=2, alpha=0.3)
ax.text(85, 45.5, 'REST API', fontsize=9, fontweight='bold', color='red', 
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='red'))

plt.tight_layout()
plt.savefig('class_diagram.jpg', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print("✅ Diagram klas zapisany jako 'class_diagram.jpg'")
plt.close()
