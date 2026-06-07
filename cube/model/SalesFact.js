cube('SalesFact', {
  sql: `SELECT * FROM fact.sales_fact`,

  joins: {
    HcpMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.hcp_id = ${HcpMaster}.hcp_id`,
    },
    ProductMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.product_id = ${ProductMaster}.product_id`,
    },
    HospitalMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.hospital_id = ${HospitalMaster}.hospital_id`,
    },
    TerritoryMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.territory_id = ${TerritoryMaster}.territory_id`,
    },
    SalesRepMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.rep_id = ${SalesRepMaster}.rep_id`,
    },
  },

  measures: {
    count: {
      type: 'count',
      description: 'Number of sales transactions',
    },
    totalSales: {
      sql: 'net_sales',
      type: 'sum',
      format: 'currency',
      description: 'Total net sales revenue in INR. Business definition: sum of net_sales after discounts.',
    },
    grossSales: {
      sql: 'gross_sales',
      type: 'sum',
      format: 'currency',
      description: 'Total gross sales before discounts',
    },
    unitsSold: {
      sql: 'units_sold',
      type: 'sum',
      description: 'Total units sold',
    },
    avgDiscountPct: {
      sql: 'discount_pct',
      type: 'avg',
      description: 'Average discount percentage',
    },
    avgOrderValue: {
      sql: 'net_sales',
      type: 'avg',
      format: 'currency',
      description: 'Average net sales per transaction',
    },
    productPerformance: {
      sql: 'net_sales',
      type: 'sum',
      format: 'currency',
      description: 'Product performance: net sales ranked by product',
    },
    territoryPerformance: {
      sql: 'net_sales',
      type: 'sum',
      format: 'currency',
      description: 'Territory performance: net sales ranked by territory',
    },
    hcpPerformance: {
      sql: 'net_sales',
      type: 'sum',
      format: 'currency',
      description: 'HCP performance: net sales attributed to healthcare professional',
    },
  },

  dimensions: {
    salesId: {
      sql: 'sales_id',
      type: 'number',
      primaryKey: true,
    },
    saleDate: {
      sql: 'sale_date',
      type: 'time',
      description: 'Date of sale transaction',
    },
    productId: {
      sql: 'product_id',
      type: 'string',
    },
    hcpId: {
      sql: 'hcp_id',
      type: 'string',
    },
    hospitalId: {
      sql: 'hospital_id',
      type: 'string',
    },
    territoryId: {
      sql: 'territory_id',
      type: 'string',
    },
    repId: {
      sql: 'rep_id',
      type: 'string',
    },
    channel: {
      sql: 'channel',
      type: 'string',
      description: 'Sales channel: Direct, Distributor, etc.',
    },
  },

  preAggregations: {
    monthlySales: {
      measures: [SalesFact.totalSales, SalesFact.unitsSold, SalesFact.grossSales],
      dimensions: [ProductMaster.therapeuticArea, TerritoryMaster.territoryName],
      timeDimension: SalesFact.saleDate,
      granularity: 'month',
      refreshKey: {
        every: '1 hour',
      },
    },
  },
});
