/**
 * Add clickable anchor links to all headings with IDs
 * Creates a # link that appears on hover
 */
document.addEventListener('DOMContentLoaded', function() {
  // Select all headings (h1-h6) that have an id attribute
  const headings = document.querySelectorAll('h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]');
  
  headings.forEach(function(heading) {
    // Create the anchor link
    const anchor = document.createElement('a');
    anchor.className = 'header-anchor';
    anchor.href = '#' + heading.id;
    anchor.innerHTML = '#';
    anchor.setAttribute('aria-label', 'Link to this section');
    
    // Add the anchor to the heading
    heading.appendChild(anchor);
  });
});
