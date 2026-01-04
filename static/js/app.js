// app.js - FINAL VERSION with State Management (FIXED)
document.addEventListener('DOMContentLoaded', () => {

  // Ambil elemen-elemen penting
  const messages = document.getElementById('messages');
  const userInput = document.getElementById('user-input');
  const sendBtn = document.getElementById('send-btn');
  const clearBtn = document.getElementById('clear-btn');
  const chatHelper = document.getElementById('chat-helper');
  const promptBar = document.getElementById('suggested-prompts-bar');

  // STATE MANAGEMENT
  let excludedNames = [];
  let lastRecommendations = [];
  let lastGenre = [];

  // Kumpulin semua modal
  const modals = {
    genre: document.getElementById('genre-modal'),
    theme: document.getElementById('theme-modal'),
    avatar: document.getElementById('avatar-modal'),
    detail: document.getElementById('anime-detail-modal')
  };

  // Fungsi buka/tutup modal
  function openModal(modal) {
    modal.classList.add('open');
  }

  function closeModal(modal) {
    modal.classList.remove('open');
  }

  // Event listener modal genre
  document.getElementById('btn-genre').addEventListener('click', () => openModal(modals.genre));
  modals.genre.querySelector('.close').addEventListener('click', () => closeModal(modals.genre));

  // Event listener modal tema
  document.getElementById('btn-theme').addEventListener('click', () => openModal(modals.theme));
  modals.theme.querySelector('.close').addEventListener('click', () => closeModal(modals.theme));

  // Event listener modal avatar
  document.querySelector('.header-avatar').addEventListener('click', () => openModal(modals.avatar));
  document.getElementById('close-modal').addEventListener('click', () => closeModal(modals.avatar));

  // Event listener modal detail anime
  document.querySelector('.anime-detail-close').addEventListener('click', () => closeModal(modals.detail));

  // Tutup modal kalo klik backdrop
  Object.values(modals).forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal(modal);
    });
  });

  // Fungsi kirim pesan
  async function sendMessage() {
    const msg = userInput.value.trim();
    if (!msg) return;

    // Sembunyiin helper dan suggestion bar
    chatHelper.style.display = 'none';
    promptBar.classList.add('hidden');

    // Bikin pesan user
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-message user';
    userMsg.textContent = msg;
    messages.appendChild(userMsg);

    // Kosongin input
    userInput.value = '';

    // Scroll ke bawah
    messages.scrollTop = messages.scrollHeight;

    try {
      // Kirim request ke server dengan state
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: msg,
          excluded_names: excludedNames,
          last_recommendations: lastRecommendations,
          last_genre: lastGenre
        })
      });

      const data = await response.json();

      // UPDATE STATE dari response backend
      if (data.excluded_names) {
        excludedNames = data.excluded_names;
        console.log('Updated excludedNames:', excludedNames);
      }

      if (data.last_genre) {
        lastGenre = data.last_genre;
        console.log('Updated lastGenre:', lastGenre);
      }

      // Bikin pesan bot (LANGSUNG MUNCUL dengan fade-in)
      const botMsg = document.createElement('div');
      botMsg.className = 'chat-message bot';
      botMsg.style.opacity = '0';
      botMsg.innerHTML = data.reply;
      messages.appendChild(botMsg);

      // Fade-in animation
      setTimeout(() => {
        botMsg.style.transition = 'opacity 0.3s ease';
        botMsg.style.opacity = '1';
      }, 10);

      // Parse dan simpen lastRecommendations dari response
      parseAndSaveRecommendations(botMsg);

      // Attach event listener ke tombol detail
      attachDetailButtons();

      // Scroll ke bawah
      messages.scrollTop = messages.scrollHeight;

    } catch (error) {
      console.error('Error:', error);
      const errorMsg = document.createElement('div');
      errorMsg.className = 'chat-message bot';
      errorMsg.textContent = '⚠️ Gagal terhubung ke server';
      messages.appendChild(errorMsg);
    }
  }

  // Fungsi parse dan simpen recommendations dari bot response
  function parseAndSaveRecommendations(botMsgElement) {
    // Extract recommendations dari detail buttons
    const detailButtons = botMsgElement.querySelectorAll('.detail-btn');

    if (detailButtons.length > 0) {
      lastRecommendations = [];
      detailButtons.forEach(btn => {
        const dataStr = btn.getAttribute('data-anime');
        if (dataStr) {
          try {
            const anime = JSON.parse(dataStr.replace(/&quot;/g, '"'));
            lastRecommendations.push(anime);
          } catch (e) {
            console.error('Error parsing anime data:', e);
          }
        }
      });
      console.log('Updated lastRecommendations:', lastRecommendations.length, 'anime');
    }
  }

  // Event listener tombol kirim
  sendBtn.addEventListener('click', sendMessage);

  // Event listener Enter key
  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });

  // Fungsi attach event listener ke tombol detail
  function attachDetailButtons() {
    document.querySelectorAll('.detail-btn:not([data-listener])').forEach(btn => {
      btn.addEventListener('click', function () {
        const dataStr = this.getAttribute('data-anime');
        if (!dataStr) return;

        const data = JSON.parse(dataStr.replace(/&quot;/g, '"'));

        // Isi modal detail
        document.getElementById('detail-name').textContent = data.name || 'Tidak tersedia';
        document.getElementById('detail-english-name').textContent = data.english_name || 'Tidak tersedia';
        document.getElementById('detail-genres').textContent = data.genres || 'Tidak ada';
        document.getElementById('detail-themes').textContent = data.themes || 'Tidak ada';
        document.getElementById('detail-score').textContent = data.score || 'Tidak tersedia';
        document.getElementById('detail-episodes').textContent = data.episodes || 'Tidak tersedia';
        document.getElementById('detail-duration').textContent = data.duration || 'Tidak tersedia';
        document.getElementById('detail-premiered').textContent = data.premiered || 'Tidak tersedia';
        document.getElementById('detail-synopsis').textContent = data.synopsis || 'Sinopsis tidak tersedia';
        document.getElementById('detail-image').src = data.image_url || '';
        document.getElementById('detail-mal-link').href = data.anime_url || '#';

        openModal(modals.detail);
      });

      btn.dataset.listener = 'true';
    });
  }

  // Event listener tombol clear
  clearBtn.addEventListener('click', () => {
    if (confirm('Yakin ingin menghapus semua chat?\nHalaman akan dimuat ulang dan semua chat akan terhapus')) {
      window.location.reload();
    }
  });

  // Event listener suggestion chips
  document.querySelectorAll('.prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      userInput.value = chip.getAttribute('data-prompt');
      sendMessage();
    });
  });
});