function handleCredentialResponse(response) {
    console.log('Encoded JWT ID token: ' + response.credential);
    // Hier können Sie die Google-Authentifizierungsantwort verarbeiten
}

// Laden Sie die Google API-Bibliothek
(function() {
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    document.head.appendChild(script);
})();
