(function () {
  'use strict';

  var btn = document.getElementById('family-tree-pdf-btn');
  if (!btn) return;

  var HTML2CANVAS =
    'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
  var JSPDF =
    'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.2/jspdf.umd.min.js';

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

  async function downloadPdf() {
    var canvasEl = document.querySelector('.family-tree-canvas');
    if (!canvasEl) return;

    setLoading(true);

    try {
      await waitForLayout();
      await loadScript(HTML2CANVAS);
      await loadScript(JSPDF);

      var pan = document.querySelector('.family-tree-pan');
      var bg = pan ? getComputedStyle(pan).backgroundColor : '#ffffff';

      var shot = await window.html2canvas(canvasEl, {
        scale: 2,
        backgroundColor: bg,
        logging: false,
        useCORS: true,
        width: canvasEl.scrollWidth,
        height: canvasEl.scrollHeight,
        windowWidth: canvasEl.scrollWidth,
        windowHeight: canvasEl.scrollHeight,
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
      setLoading(false);
    }
  }

  btn.addEventListener('click', downloadPdf);
})();
