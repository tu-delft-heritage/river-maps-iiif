import type { Point } from './georeference-export.ts';

// Screening limits, not estimates of survey accuracy. Natural scan variation in
// this collection is much smaller; the original bad fits had ratios of 1.23–1.28.
export const shapeLimits = {maxPrincipalScaleRatio: 1.02, maxGridSkewDegrees: 1};

export function shapeDiagnostics(linear: [Point, Point]) {
  if (linear.length !== 2 || linear.some(row => row.length !== 2 || row.some(v => !Number.isFinite(v))))
    throw new Error('Shape screening requires a finite 2×2 transform');
  const [[a,b],[c,d]] = linear;
  const determinant = a*d-b*c;
  const eastScale = Math.hypot(a,c), northScale = Math.hypot(b,d);
  if (!eastScale || !northScale || !determinant) throw new Error('Singular image transform');
  const dot = a*b+c*d;
  const trace = eastScale**2+northScale**2;
  const discriminant = Math.hypot(eastScale**2-northScale**2,2*dot);
  const largest = Math.sqrt((trace+discriminant)/2);
  const smallest = Math.abs(determinant)/largest;
  const principalScaleRatio = largest/smallest;
  const gridAngleDegrees = Math.acos(Math.max(-1,Math.min(1,dot/(eastScale*northScale))))*180/Math.PI;
  const gridSkewDegrees = Math.abs(90-gridAngleDegrees);
  // RD has north-positive y; raster pixels have down-positive y. Negative
  // determinant is therefore the expected orientation for an unmirrored scan.
  const mirrored = determinant > 0;
  const flags = [
    ...(mirrored ? ['mirrored-grid'] : []),
    ...(principalScaleRatio > shapeLimits.maxPrincipalScaleRatio ? ['directional-stretch-over-2pct'] : []),
    ...(gridSkewDegrees > shapeLimits.maxGridSkewDegrees ? ['grid-skew-over-1deg'] : []),
  ];
  return {determinant,mirrored,principalScaleRatio,gridAngleDegrees,gridSkewDegrees,
    eastPixelsPerMetre:eastScale,northPixelsPerMetre:northScale,flags};
}
