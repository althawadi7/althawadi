(function () {
  'use strict';

  var btn = document.getElementById('family-tree-pdf-btn');
  if (!btn) return;

  var HTML2CANVAS =
    'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
  var JSPDF =
    'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.2/jspdf.umd.min.js';

  var PDF = {
    panBg: '#f0e8dc',
    dot: 'rgba(90, 70, 50, 0.1)',
    card: '#f5efe3',
    cardHi: '#faf0d4',
    cardFocus: '#fff8ee',
    cardBorder: '#c9a56a',
    cardBorderHi: '#c9952a',
    cardBorderFocus: '#b45309',
    cardShadow: 'rgba(80, 55, 30, 0.12)',
    text: '#3d2810',
    pat: '#6b5344',
    line: '#9a6848',
    joint: '#b87850',
  };

  var COLOR_PROPS = [
    'color',
    'backgroundColor',
    'borderColor',
    'borderTopColor',
    'borderRightColor',
    'borderBottomColor',
    'borderLeftColor',
    'outlineColor',
    'textDecorationColor',
    'fill',
    'stroke',
  ];

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (document.querySelector('script[src="' + src + '"]')) {
        resolve();
        return;
      }
      var script = document.createElement('script');
      script.src = src;
      script.onload = resolve;
      script.onerror = function () {
        reject(new Error('Failed to load ' + src));
      };
      document.head.appendChild(script);
    });
  }

  function waitForLayout() {
    return new Promise(function (resolve) {
      if (typeof window.__familyTreeLayout === 'function') {
        window.__familyTreeLayout();
      }
      requestAnimationFrame(function () {
        requestAnimationFrame(resolve);
      });
    });
  }

  function setLoading(loading) {
    btn.disabled = loading;
    btn.setAttribute('aria-busy', loading ? 'true' : 'false');
    var label = btn.querySelector('.family-tree-pdf-label');
    if (!label) return;
    if (loading) {
      if (!label.dataset.defaultLabel) {
        label.dataset.defaultLabel = label.textContent;
      }
      label.textContent = 'جاري التحميل…';
    } else if (label.dataset.defaultLabel) {
      label.textContent = label.dataset.defaultLabel;
    }
  }

  function hasUnsafeColor(val) {
    if (!val || val === 'none' || val === 'transparent' || val === 'inherit') return false;
    return /oklch|color-mix|color\(/i.test(val);
  }

  function toSafeColor(value, fallback) {
    if (!value || value === 'none') return fallback || 'transparent';
    if (!hasUnsafeColor(value)) return value;
    var probe = document.createElement('span');
    probe.style.cssText =
      'position:absolute;visibility:hidden;pointer-events:none;left:-99999px;top:0;';
    probe.style.color = fallback || '#000000';
    probe.style.color = value;
    document.body.appendChild(probe);
    var rgb = getComputedStyle(probe).color;
    document.body.removeChild(probe);
    return rgb && rgb !== 'rgba(0, 0, 0, 0)' ? rgb : fallback || '#000000';
  }

  function sanitizeStyleValue(prop, value) {
    if (!value) return value;
    if (prop === 'boxShadow' || prop === 'background' || prop === 'backgroundImage') {
      if (!hasUnsafeColor(value)) return value;
      if (prop === 'boxShadow') return '0 2px 0 ' + PDF.cardShadow;
      if (prop === 'backgroundImage') {
        return (
          'radial-gradient(circle, ' + PDF.dot + ' 1px, transparent 1px)'
        );
      }
      return toSafeColor(value, PDF.panBg);
    }
    if (COLOR_PROPS.indexOf(prop) !== -1 || hasUnsafeColor(value)) {
      return toSafeColor(value, PDF.text);
    }
    return value;
  }

  function detachStylesheets() {
    var saved = [];
    document.querySelectorAll('link[rel="stylesheet"], style').forEach(function (node) {
      saved.push({ node: node, parent: node.parentNode, next: node.nextSibling });
      node.parentNode.removeChild(node);
    });
    return saved;
  }

  function restoreStylesheets(saved) {
    saved.forEach(function (entry) {
      if (!entry.parent) return;
      if (entry.next && entry.next.parentNode === entry.parent) {
        entry.parent.insertBefore(entry.node, entry.next);
      } else {
        entry.parent.appendChild(entry.node);
      }
    });
  }

  function applyPdfPaint(pan) {
    var saved = [];

    function remember(el) {
      saved.push({ el: el, cssText: el.style.cssText });
    }

    remember(pan);
    saved[saved.length - 1].hadPdfClass = pan.classList.contains('family-tree-pdf-mode');
    pan.classList.add('family-tree-pdf-mode');
    pan.style.backgroundColor = PDF.panBg;
    pan.style.backgroundImage =
      'radial-gradient(circle, ' + PDF.dot + ' 1px, transparent 1px)';
    pan.style.backgroundSize = '18px 18px';

    pan.querySelectorAll('.family-tree-node, .family-tree-node--link').forEach(function (node) {
      remember(node);
      var isRoot = node.classList.contains('is-root');
      var isFocus = node.classList.contains('is-focus');
      node.style.background = isRoot
        ? PDF.cardHi
        : isFocus
          ? PDF.cardFocus
          : PDF.card;
      node.style.borderColor = isRoot
        ? PDF.cardBorderHi
        : isFocus
          ? PDF.cardBorderFocus
          : PDF.cardBorder;
      node.style.borderStyle = 'solid';
      node.style.borderWidth = '1px';
      node.style.borderRadius = '10px';
      node.style.boxShadow = '0 2px 6px ' + PDF.cardShadow;
      node.style.color = PDF.text;
    });

    pan.querySelectorAll('.family-tree-given').forEach(function (el) {
      remember(el);
      el.style.color = PDF.text;
    });

    pan.querySelectorAll('.family-tree-pat').forEach(function (el) {
      remember(el);
      el.style.color = PDF.pat;
    });

    pan.querySelectorAll('.family-tree-lines path').forEach(function (path) {
      remember(path);
      path.setAttribute('stroke', PDF.line);
      path.setAttribute('fill', 'none');
      path.style.stroke = PDF.line;
      path.style.fill = 'none';
    });

    pan.querySelectorAll('.family-tree-lines circle').forEach(function (dot) {
      remember(dot);
      dot.setAttribute('fill', PDF.joint);
      dot.style.fill = PDF.joint;
    });

    return saved;
  }

  function restorePdfPaint(saved) {
    saved.forEach(function (entry) {
      entry.el.style.cssText = entry.cssText;
      if (entry.el.classList.contains('family-tree-pdf-mode') && !entry.hadPdfClass) {
        entry.el.classList.remove('family-tree-pdf-mode');
      }
    });
  }

  function sanitizeCloneTree(root) {
    root.querySelectorAll('*').forEach(function (el) {
      if (!el.style) return;
      var i;
      for (i = 0; i < el.style.length; i += 1) {
        var prop = el.style[i];
        var val = el.style.getPropertyValue(prop);
        if (hasUnsafeColor(val)) {
          el.style.setProperty(prop, sanitizeStyleValue(prop, val));
        }
      }
      if (el.hasAttribute('stroke') && hasUnsafeColor(el.getAttribute('stroke'))) {
        el.setAttribute('stroke', PDF.line);
      }
      if (el.hasAttribute('fill') && hasUnsafeColor(el.getAttribute('fill'))) {
        el.setAttribute('fill', 'none');
      }
    });
  }

  async function downloadPdf() {
    var pan = document.querySelector('.family-tree-pan');
    if (!pan) return;

    setLoading(true);
    var savedPaint = [];
    var detachedSheets = [];

    try {
      await waitForLayout();
      await loadScript(HTML2CANVAS);
      await loadScript(JSPDF);

      savedPaint = applyPdfPaint(pan);
      detachedSheets = detachStylesheets();

      var shot = await window.html2canvas(pan, {
        scale: 2,
        backgroundColor: PDF.panBg,
        logging: false,
        useCORS: true,
        width: pan.scrollWidth,
        height: pan.scrollHeight,
        windowWidth: pan.scrollWidth,
        windowHeight: pan.scrollHeight,
        onclone: function (clonedDoc) {
          clonedDoc.querySelectorAll('link[rel="stylesheet"], style').forEach(function (node) {
            if (node.parentNode) node.parentNode.removeChild(node);
          });
          var clonePan = clonedDoc.querySelector('.family-tree-pan');
          if (clonePan) sanitizeCloneTree(clonePan);
        },
      });

      var jsPDF = window.jspdf.jsPDF;
      var pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
      var pageW = pdf.internal.pageSize.getWidth();
      var pageH = pdf.internal.pageSize.getHeight();
      var margin = 8;
      var usableW = pageW - margin * 2;
      var usableH = pageH - margin * 2;

      var imgData = shot.toDataURL('image/jpeg', 0.92);
      var pdfImgH = (shot.height * usableW) / shot.width;
      var heightLeft = pdfImgH;
      var y = margin;

      pdf.addImage(imgData, 'JPEG', margin, y, usableW, pdfImgH);
      heightLeft -= usableH;

      while (heightLeft > 0) {
        y = margin - (pdfImgH - heightLeft);
        pdf.addPage('a4', 'landscape');
        pdf.addImage(imgData, 'JPEG', margin, y, usableW, pdfImgH);
        heightLeft -= usableH;
      }

      pdf.save('shajarat-al-thawadi.pdf');
    } catch (err) {
      console.error(err);
      window.alert('تعذّر إنشاء PDF. حاول مرة أخرى.');
    } finally {
      restoreStylesheets(detachedSheets);
      restorePdfPaint(savedPaint);
      if (typeof window.__familyTreeLayout === 'function') {
        window.__familyTreeLayout();
      }
      setLoading(false);
    }
  }

  btn.addEventListener('click', downloadPdf);
})();
