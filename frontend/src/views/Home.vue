<template>
  <div class="home">
    <header class="hero">
      <h1>Enhanced Spotify App</h1>
      <p>Odkryj swoje muzyczne preferencje i stwórz unikalne playlisty</p>
      <div class="cta-buttons">
        <router-link to="/login" class="btn btn-primary">Zaloguj się</router-link>
        <router-link to="/register" class="btn btn-secondary">Zarejestruj się</router-link>
      </div>
    </header>

    <section class="features">
      <div class="feature">
        <h3>📊 Statystyki</h3>
        <p>Zobacz swoje osobiste statystyki słuchania muzyki</p>
      </div>
      <div class="feature">
        <h3>🗺️ Mapa słuchania</h3>
        <p>Interaktywna mapa twoich muzycznych podróży</p>
      </div>
      <div class="feature">
        <h3>🎵 Playlisty</h3>
        <p>Twórz playlisty z wybranego okresu czasu</p>
      </div>
    </section>
  </div>
</template>

<script setup>
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.hero {
  text-align: center;
  padding: 4rem 0;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #1db954;
}

.hero p {
  font-size: 1.5rem;
  margin-bottom: 2rem;
  color: #666;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 1rem 2rem;
  border-radius: 2rem;
  text-decoration: none;
  font-weight: bold;
  transition: transform 0.2s;
}

.btn:hover {
  transform: scale(1.05);
}

.btn-primary {
  background-color: #1db954;
  color: white;
}

.btn-secondary {
  background-color: #191414;
  color: white;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 4rem;
}

.feature {
  padding: 2rem;
  border-radius: 1rem;
  background-color: #f9f9f9;
  text-align: center;
}

.feature h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}
</style>
