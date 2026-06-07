view('ExecutiveDashboard', {
  description: 'Pre-joined view for executive analytics queries',

  cubes: [
    {
      join_path: SalesFact,
      includes: [
        'totalSales',
        'grossSales',
        'unitsSold',
        'hcpPerformance',
        'territoryPerformance',
        'productPerformance',
        'saleDate',
        'channel',
      ],
    },
    {
      join_path: SalesFact.ProductMaster,
      includes: ['productName', 'brandName', 'therapeuticArea', 'indication'],
    },
    {
      join_path: SalesFact.HcpMaster,
      includes: ['fullName', 'specialty', 'tier', 'city', 'isKol'],
    },
    {
      join_path: SalesFact.TerritoryMaster,
      includes: ['territoryName', 'region', 'zone'],
    },
    {
      join_path: SalesFact.HospitalMaster,
      includes: ['hospitalName', 'hospitalType'],
    },
    {
      join_path: SalesFact.SalesRepMaster,
      includes: ['fullName'],
    },
    {
      join_path: PrescriptionFact,
      prefix: true,
      includes: ['prescriptionCount', 'newPrescriptionCount', 'rxDate'],
    },
    {
      join_path: PrescriptionFact.HcpMaster,
      prefix: true,
      includes: ['specialty', 'tier', 'city'],
    },
    {
      join_path: PrescriptionFact.ProductMaster,
      prefix: true,
      includes: ['therapeuticArea', 'productName'],
    },
  ],
});
