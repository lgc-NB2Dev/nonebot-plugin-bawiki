// https://github.com/nulla2011/bluearchive-logo/blob/master/src/canvas.ts
/** @param {[string, string]} */
async ([textL, textR]) => {
  const transparentBg = true;
  const fontSize = 84;
  const canvasHeight = 250;
  const canvasWidth = 50;
  const textBaseLine = 0.68;
  const horizontalTilt = -0.4;
  const paddingX = 10;
  const graphOffset = { X: -15, Y: 0 };
  const hollowPath = [
    [284, 136],
    [321, 153],
    [159, 410],
    [148, 403],
  ];

  const halo = document.createElement('img');
  halo.id = 'halo';
  halo.src = 'https://bawiki.res/halo.png';

  const cross = document.createElement('img');
  cross.id = 'cross';
  cross.src = 'https://bawiki.res/cross.png';

  // wait images loaded
  await Promise.all(
    [halo, cross].map(
      (img) =>
        new Promise((resolve, reject) => {
          img.onload = resolve;
          img.onerror = reject;
        })
    )
  );

  // create canvas
  const canvas = document.createElement('canvas');
  canvas.width = canvasWidth;
  canvas.height = canvasHeight;
  const c = canvas.getContext('2d');

  // load font
  const font = `${fontSize}px 'Ro GSan Serif Std B', 'Glow Sans SC Heavy', sans-serif`;
  await document.fonts.load(font, `${textL}${textR}`);
  c.font = font;

  // extend canvas
  const textMetricsL = c.measureText(textL);
  const textMetricsR = c.measureText(textR);

  const textWidthL =
    textMetricsL.width -
    (textBaseLine * canvasHeight + textMetricsL.fontBoundingBoxDescent) *
      horizontalTilt;
  const textWidthR =
    textMetricsR.width +
    (textBaseLine * canvasHeight - textMetricsR.fontBoundingBoxAscent) *
      horizontalTilt;

  const canvasWidthL =
    textWidthL + paddingX > canvasWidth / 2
      ? textWidthL + paddingX
      : canvasWidth / 2;
  const canvasWidthR =
    textWidthR + paddingX > canvasWidth / 2
      ? textWidthR + paddingX
      : canvasWidth / 2;

  canvas.width = canvasWidthL + canvasWidthR;

  // clear canvas
  c.clearRect(0, 0, canvas.width, canvas.height);

  // background
  if (!transparentBg) {
    c.fillStyle = '#fff';
    c.fillRect(0, 0, canvas.width, canvas.height);
  }

  // left blue text
  c.font = font;
  c.fillStyle = '#128AFA';
  c.textAlign = 'end';
  c.setTransform(1, 0, horizontalTilt, 1, 0, 0);
  c.fillText(textL, canvasWidthL, canvas.height * textBaseLine);
  c.resetTransform(); // restore don't work

  // halo
  c.drawImage(
    halo,
    canvasWidthL - canvas.height / 2 + graphOffset.X,
    graphOffset.Y,
    canvasHeight,
    canvasHeight
  );

  // right black text
  c.fillStyle = '#2B2B2B';
  c.textAlign = 'start';
  if (transparentBg) c.globalCompositeOperation = 'destination-out';
  c.strokeStyle = 'white';
  c.lineWidth = 12;
  c.setTransform(1, 0, horizontalTilt, 1, 0, 0);
  c.strokeText(textR, canvasWidthL, canvas.height * textBaseLine);

  c.globalCompositeOperation = 'source-over';
  c.fillText(textR, canvasWidthL, canvas.height * textBaseLine);
  c.resetTransform();

  // cross stroke
  const graph = {
    X: canvasWidthL - canvas.height / 2 + graphOffset.X,
    Y: graphOffset.Y,
  };
  c.beginPath();
  hollowPath.forEach(([x, y], i) => {
    const f = (i === 0 ? c.moveTo : c.lineTo).bind(c);
    f(graph.X + x / 2, graph.Y + y / 2);
  });
  c.closePath();

  if (transparentBg) c.globalCompositeOperation = 'destination-out';
  c.fillStyle = 'white';
  c.fill();
  c.globalCompositeOperation = 'source-over';

  // cross
  c.drawImage(
    cross,
    canvasWidthL - canvas.height / 2 + graphOffset.X,
    graphOffset.Y,
    canvasHeight,
    canvasHeight
  );

  // output
  /** @type {HTMLCanvasElement} */
  let outputCanvas;
  if (
    textWidthL + paddingX >= canvasWidth / 2 &&
    textWidthR + paddingX >= canvasWidth / 2
  ) {
    outputCanvas = canvas;
  } else {
    outputCanvas = document.createElement('canvas');
    outputCanvas.width = textWidthL + textWidthR + paddingX * 2;
    outputCanvas.height = canvas.height;

    const ctx = outputCanvas.getContext('2d');
    ctx.drawImage(
      canvas,
      canvasWidth / 2 - textWidthL - paddingX,
      0,
      textWidthL + textWidthR + paddingX * 2,
      canvas.height,
      0,
      0,
      textWidthL + textWidthR + paddingX * 2,
      canvas.height
    );
  }

  const b64 = outputCanvas.toDataURL().replace(/^data:image\/png;base64,/, '');
  return `base64://${b64}`;
};
