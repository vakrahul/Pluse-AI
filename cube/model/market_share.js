view('MarketShare', {
  description: 'Market share analysis: product sales as percentage of therapeutic area total',

  cubes: [
    {
      join_path: SalesFact,
      includes: ['totalSales', 'saleDate'],
    },
    {
      join_path: SalesFact.ProductMaster,
      includes: ['productName', 'brandName', 'therapeuticArea'],
    },
    {
      join_path: SalesFact.TerritoryMaster,
      includes: ['territoryName', 'region'],
    },
  ],
});
