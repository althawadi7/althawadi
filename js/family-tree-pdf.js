(function () {
  'use strict';

  var btn = document.getElementById('family-tree-pdf-btn');
  if (!btn) return;

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
  };

  var HTML2CANVAS_SRCS = [
    'js/vendor/html2canvas.min.js',
    'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js',
    'https://unpkg.com/html2canvas@1.4.1/dist/html2canvas.min.js',
  ];

  var JSPDF_SRCS = [
    'js/vendor/jspdf.umd.min.js',
    'https://cdn.jsdelivr.net/npm/jspdf@2.5.2/dist/jspdf.umd.min.js',
    'https://unpkg.com/jspdf@2.5.2/dist/jspdf.umd.min.js',
  ];

  function assetBase() {
    if (window.__althawadiBase) return window.__althawadiBase;
    if (location.pathname.indexOf('/althawadi/') !== -1) return '/althawadi/';
    return '../';
  }

  function resolveUrl(path) {
    return path.indexOf('://') !== -1 ? path : assetBase() + path;
  }

  function loadLib(urls, isReady) {
    if (isReady()) return Promise.resolve();

    function tryIndex(i) {
      if (isReady()) return Promise.resolve();
      if (i >= urls.length) {
        return Promise.reject(new Error('تعذّر تحميل المكتبة المطلوبة للـ PDF'));
      }

      var url = resolveUrl(urls[i]);
      return new Promise(function (resolve, reject) {
        var tag = document.createElement('script');
        tag.src = url;
        tag.async = true;
        tag.onload = function () {
          if (isReady()) resolve();
          else {
            tag.remove();
            tryIndex(i + 1).then(resolve).catch(reject);
          }
        };
        tag.onerror = function () {
          tag.remove();
          tryIndex(i + 1).then(resolve).catch(reject);
        };
        document.head.appendChild(tag);
      });
    }

    return tryIndex(0);
  }

  function getJsPDF() {
    if (window.jspdf && window.jspdf.jsPDF) return window.jspdf.jsPDF;
    if (typeof window.jsPDF === 'function') return window.jsPDF;
    return null;
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

  function disableMainStylesheets() {
    var saved = [];
    document.querySelectorAll('link[rel="stylesheet"]').forEach(function (link) {
      saved.push({ link: link, disabled: link.disabled });
      link.disabled = true;
    });
    return saved;
  }

  function restoreMainStylesheets(saved) {
    saved.forEach(function (entry) {
      entry.link.disabled = entry.disabled;
    });
  }

  function injectCriticalCss() {
    var id = 'family-tree-pdf-critical-link';
    var existing = document.getElementById(id);
    if (existing) return Promise.resolve();

    return new Promise(function (resolve, reject) {
      var link = document.createElement('link');
      link.id = id;
      link.rel = 'stylesheet';
      link.href = resolveUrl('css/family-tree-pdf-critical.css');
      link.onload = function () {
        resolve();
      };
      link.onerror = function () {
        reject(new Error('PDF layout CSS failed'));
      };
      document.head.appendChild(link);
    });
  }

  function removeCriticalCss() {
    var link = document.getElementById('family-tree-pdf-critical-link');
    if (link && link.parentNode) link.parentNode.removeChild(link);
  }

  function beginExportMode(pan) {
    return {
      panClass: pan.classList.contains('family-tree-pdf-exporting'),
      scrollLeft: pan.scrollLeft,
      scrollTop: pan.scrollTop,
      overflow: pan.style.overflow,
      maxHeight: pan.style.maxHeight,
      height: pan.style.height,
      minHeight: pan.style.minHeight,
      width: pan.style.width,
    };
  }

  function applyExportMode(pan) {
    pan.classList.add('family-tree-pdf-exporting');
    pan.scrollLeft = 0;
    pan.scrollTop = 0;
  }

  function endExportMode(pan, saved) {
    pan.classList.remove('family-tree-pdf-exporting');
    pan.scrollLeft = saved.scrollLeft;
    pan.scrollTop = saved.scrollTop;
    pan.style.overflow = saved.overflow;
    pan.style.maxHeight = saved.maxHeight;
    pan.style.height = saved.height;
    pan.style.minHeight = saved.minHeight;
    pan.style.width = saved.width;
  }

  function paintNodesForPdf(root) {
    root.querySelectorAll('.family-tree-node, .family-tree-node--link').forEach(function (node) {
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
      node.style.display = 'inline-block';
      node.style.width = 'fit-content';
      node.style.maxWidth = '7.5rem';
    });

    root.querySelectorAll('.family-tree-given').forEach(function (el) {
      el.style.color = PDF.text;
    });

    root.querySelectorAll('.family-tree-pat').forEach(function (el) {
      el.style.color = PDF.pat;
    });

    root.querySelectorAll('.family-tree-lines line').forEach(function (line) {
      line.setAttribute('stroke', PDF.line);
      line.style.stroke = PDF.line;
    });
  }

  /** Scale tree image to fit one A4 landscape page; returns draw box in mm. */
  function pageDrawBox(shot, pageW, pageH, margin) {
    var usableW = pageW - margin * 2;
    var usableH = pageH - margin * 2;
    var drawW = usableW;
    var drawH = (shot.height * drawW) / shot.width;

    if (drawH > usableH) {
      drawH = usableH;
      drawW = (shot.width * drawH) / shot.height;
    }

    return {
      x: (pageW - drawW) / 2,
      y: (pageH - drawH) / 2,
      w: drawW,
      h: drawH,
      usableH: usableH,
    };
  }

  function addImagePages(pdf, imgData, shot, margin) {
    var pageW = pdf.internal.pageSize.getWidth();
    var pageH = pdf.internal.pageSize.getHeight();
    var box = pageDrawBox(shot, pageW, pageH, margin);

    if (box.h <= box.usableH + 0.5) {
      pdf.addImage(imgData, 'JPEG', box.x, box.y, box.w, box.h);
      return;
    }

    var usableW = pageW - margin * 2;
    var drawW = usableW;
    var drawH = (shot.height * drawW) / shot.width;
    var heightLeft = drawH;
    var y = margin;

    pdf.addImage(imgData, 'JPEG', margin, y, drawW, drawH);
    heightLeft -= box.usableH;

    while (heightLeft > 0) {
      y = margin - (drawH - heightLeft);
      pdf.addPage('a4', 'landscape');
      pdf.addImage(imgData, 'JPEG', margin, y, drawW, drawH);
      heightLeft -= box.usableH;
    }
  }

  function clearInlinePaint(root) {
    root.querySelectorAll('[style]').forEach(function (el) {
      if (
        el.classList.contains('family-tree-node') ||
        el.classList.contains('family-tree-node--link') ||
        el.classList.contains('family-tree-given') ||
        el.classList.contains('family-tree-pat') ||
        el.classList.contains('family-tree-lines')
      ) {
        el.removeAttribute('style');
      }
    });
    root.querySelectorAll('.family-tree-lines line').forEach(function (line) {
      line.removeAttribute('stroke');
    });
  }

  async function downloadPdf() {
    var pan = document.querySelector('.family-tree-pan');
    var canvas = pan && pan.querySelector('.family-tree-canvas');
    if (!pan || !canvas) return;

    setLoading(true);
    var exportState = null;
    var disabledLinks = [];

    try {
      await waitForLayout();

      await loadLib(HTML2CANVAS_SRCS, function () {
        return typeof window.html2canvas === 'function';
      });
      await loadLib(JSPDF_SRCS, function () {
        return !!getJsPDF();
      });

      var JsPDF = getJsPDF();
      if (!JsPDF) throw new Error('jsPDF unavailable');

      exportState = beginExportMode(pan);
      disabledLinks = disableMainStylesheets();
      await injectCriticalCss();
      applyExportMode(pan);

      paintNodesForPdf(pan);

      if (typeof window.__familyTreeLayout === 'function') {
        window.__familyTreeLayout();
      }
      await new Promise(function (r) {
        requestAnimationFrame(function () {
          requestAnimationFrame(r);
        });
      });

      var capW = Math.ceil(canvas.scrollWidth);
      var capH = Math.ceil(canvas.scrollHeight);

      var shot = await window.html2canvas(canvas, {
        scale: 2,
        backgroundColor: PDF.panBg,
        logging: false,
        useCORS: true,
        scrollX: 0,
        scrollY: 0,
        width: capW,
        height: capH,
        windowWidth: capW,
        windowHeight: capH,
        onclone: function (clonedDoc) {
          clonedDoc.querySelectorAll('link[rel="stylesheet"]').forEach(function (node) {
            if (node.id === 'family-tree-pdf-critical-link') return;
            node.disabled = true;
          });
          var tree = clonedDoc.querySelector('.family-tree-pdf-exporting .tree');
          if (tree) {
            tree.style.transform = 'scaleX(-1)';
            tree.style.transformOrigin = 'center top';
          }
          clonedDoc
            .querySelectorAll('.family-tree-pdf-exporting .tree li > a, .family-tree-pdf-exporting .tree li > .family-tree-node')
            .forEach(function (card) {
              card.style.transform = 'scaleX(-1)';
            });
        },
      });

      var pdf = new JsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
      var margin = 8;
      var imgData = shot.toDataURL('image/jpeg', 0.92);

      addImagePages(pdf, imgData, shot, margin);
      pdf.save('shajarat-al-thawadi.pdf');
    } catch (err) {
      console.error(err);
      window.alert('تعذّر إنشاء PDF. حدّث الصفحة وحاول مرة أخرى.');
    } finally {
      if (pan && exportState) {
        clearInlinePaint(pan);
        endExportMode(pan, exportState);
      }
      removeCriticalCss();
      restoreMainStylesheets(disabledLinks);
      if (typeof window.__familyTreeLayout === 'function') {
        window.__familyTreeLayout();
      }
      setLoading(false);
    }
  }

  btn.addEventListener('click', downloadPdf);
})();
