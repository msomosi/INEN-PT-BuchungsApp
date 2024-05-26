function Logo() {
    const img = document.createElement('img');
    img.src = './assets/logo.png'; // Path to the logo image
    img.className = 'logo';
    return img;
  }
  
  document.addEventListener('DOMContentLoaded', () => {
    const root = document.getElementById('root');
    const header = Logo();
    root.appendChild(header);
  });
  