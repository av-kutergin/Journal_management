window.addEventListener('load', function() {
  if (window.getComputedStyle(document.body).pointerEvents === undefined || window.getComputedStyle(document.body).mixBlendMode === undefined) {
    var elements = document.getElementsByClassName('wrapper');
    for (i=0; i<elements.length; i++) {
      elements[i].className = elements[i].className + ' ' + 'wrapper_noglitch'
    }
  }
})