export const defaultBaseUrl = 'https://tu-delft-heritage.github.io/river-maps-iiif/';

export interface Series {
  slug: string;
  label: string;
  source: string;
}

export interface Edition {
  slug: string;
  label: string;
  series: Series[];
}

// Add future editions as siblings. Slugs form permanent public URLs.
export const editions: Edition[] = [
  {
    slug: 'first-edition',
    label: 'First edition',
    series: [
      {
        slug: 'series-1',
        label: 'Series 1 — Boven Rijn, de Waal, de Merwede, de Oude en een gedeelte van de Nieuwe Maas, van Lobith tot Brielle',
        source: 'https://objects.library.uu.nl/manifest/iiif/v3/20.500.14918-462061',
      },
      {
        slug: 'series-2',
        label: 'Series 2 — Boven en Neder-Rijn, de Lek en de Nieuwe Maas, van Lobith tot Brielle',
        source: 'https://objects.library.uu.nl/manifest/iiif/v3/20.500.14918-462106',
      },
      {
        slug: 'series-3',
        label: 'Series 3 — IJssel van Westervoort tot Kampen',
        source: 'https://objects.library.uu.nl/manifest/iiif/v3/20.500.14918-462062',
      },
      {
        slug: 'series-4',
        label: 'Series 4 — Boven Maas van Visé tot Woudrichem',
        source: 'https://objects.library.uu.nl/manifest/iiif/v3/20.500.14918-462072',
      },
      {
        slug: 'series-5',
        label: 'Series 5 — Oude en Nieuwe Merwede en de killen in het Bergsche Veld',
        source: 'https://objects.library.uu.nl/manifest/iiif/v3/20.500.14918-462108',
      },
      {
        slug: 'series-6',
        label: 'Series 6 — Hollandsche IJssel van Gouda tot IJsselmonde',
        source: 'https://objects.library.uu.nl/manifest/iiif/v3/20.500.14918-462063',
      },
    ],
  },
];
