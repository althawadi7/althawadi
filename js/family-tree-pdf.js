(function () {
  'use strict';

  var btn = document.getElementById('family-tree-pdf-btn');
  if (!btn) return;

  var HTML2CANVAS =
    'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
  var JSPDF =
    'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.2/jspdf.umd.min.js';

  var STYLE_PROPS = [
    'color',
    'backgroundColor',
    'borderTopWidth',
    'borderTopStyle',
    'borderTopColor',
    'borderRightWidth',
    'borderRightStyle',
    'borderRightColor',
    'borderBottomWidth',
    'borderBottomStyle',
    'borderBottomColor',
    'borderLeftWidth',
    'borderLeftStyle',
    'borderLeftColor',
    'borderRadius',
    'boxShadow',
    'fontSize',
    'fontFamily',
    'fontWeight',
    'paddingTop',
    'paddingRight',
    'paddingBottom',
    'paddingLeft',
    'marginTop',
    'marginRight',
    'marginBottom',
    'marginLeft',
    'width',
    'height',
    'minWidth',
    'maxWidth',
    'display',
    'flexDirection',
    'flexWrap',
    'alignItems',
    'justifyContent',
    'gap',
    'textAlign',
    'lineHeight',
    'boxSizing',
    'position',
    'transform',
    'left',
    'top',
    'direction',
    'whiteSpace',
    'wordBreak',
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

  function inlineTreeStyles(root) {
    var saved = [];
    var all = [root].concat(Array.prototype.slice.call(root.querySelectorAll('*')));
    all.forEach(function (el) {
      saved.push({ el: el, cssText: el.style.cssText });
      var cs = getComputedStyle(el);
      STYLE_PROPS.forEach(function (prop) {
        var val = cs[prop];
        if (val) el.style[prop] = val;
      });
      if (cs.borderTopWidth !== '0px') {
        el.style.border =
          cs.borderTopWidth + ' ' + cs.borderTopStyle + ' ' + cs.borderTopColor;
      }
    });

    root.querySelectorAll('path').forEach(function (path) {
      saved.push({ el: path, stroke: path.getAttribute('stroke'), sw: path.getAttribute('stroke-width') });
      var cs = getComputedStyle(path);
      path.setAttribute('stroke', cs.stroke && cs.stroke !== 'none' ? cs.stroke : '#b8654a');
      path.setAttribute('stroke-width', cs.strokeWidth || '3');
      path.setAttribute('fill', 'none');
    });

    return saved;
  }

  function restoreTreeStyles(saved) {
    saved.forEach(function (entry) {
      if (entry.cssText !== undefined) {
        entry.el.style.cssText = entry.cssText;
      }
      if (entry.stroke !== undefined) {
        if (entry.stroke) entry.el.setAttribute('stroke', entry.stroke);
        else entry.el.removeAttribute('stroke');
        if (entry.sw) entry.el.setAttribute('stroke-width', entry.sw);
        else entry.el.removeAttribute('stroke-width');
      }
    });
  }

  function disableStylesheets() {
    var toggled = [];
    document.querySelectorAll('link[rel="stylesheet"]').forEach(function (link) {
      toggled.push({ node: link, disabled: link.disabled });
      link.disabled = true;
    });
    return toggled;
  }

  function restoreStylesheets(toggled) {
    toggled.forEach(function (entry) {
      entry.node.disabled = entry.disabled;
    });
  }

  async function downloadPdf() {
    var canvasEl = document.querySelector('.family-tree-canvas');
    if (!canvasEl) return;

    setLoading(true);
    var savedStyles = [];
    var disabledSheets = [];

    try {
      await waitForLayout();
      await loadScript(HTML2CANVAS);
      await loadScript(JSPDF);

      savedStyles = inlineTreeStyles(canvasEl);
      disabledSheets = disableStylesheets();

      var shot = await window.html2canvas(canvasEl, {
        scale: 2,
        backgroundColor: '#e8e0d4',
        logging: false,
        useCORS: true,
        width: canvasEl.scrollWidth,
        height: canvasEl.scrollHeight,
        windowWidth: canvasEl.scrollWidth,
        windowHeight: canvasEl.scrollHeight,
        onclone: function (clonedDoc) {
          clonedDoc.querySelectorAll('link[rel="stylesheet"], style').forEach(function (node) {
            node.parentNode.removeChild(node);
          });
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
      restoreStylesheets(disabledSheets);
      restoreTreeStyles(savedStyles);
      if (typeof window.__familyTreeLayout === 'function') {
        window.__familyTreeLayout();
      }
      setLoading(false);
    }
  }

  btn.addEventListener('click', downloadPdf);
})();
