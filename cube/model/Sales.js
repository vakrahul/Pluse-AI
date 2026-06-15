cube(`Sales`, {
  sql: `SELECT * FROM oasis_normalized.payer_360_sales`,
  title: `Sales`,
  description: `Net sales dollars and units sold per MCO and Brand`,

  measures: {
    count: {
      type: `count`,
      title: `Sales Record Count`,
    },
    totalSalesUsd: {
      sql: `sale_amount_usd`,
      type: `sum`,
      title: `Total Sales (USD)`,
    },
    totalUnitsSold: {
      sql: `units_sold`,
      type: `sum`,
      title: `Total Units Sold`,
    },
  },

  dimensions: {
    id: {
      sql: `sale_id`,
      type: `string`,
      primaryKey: true,
    },
    mcoId: {
      sql: `mdm_mco_id`,
      type: `string`,
      title: `MCO ID`,
    },
    productBrandName: {
      sql: `product_brand_name`,
      type: `string`,
      title: `Brand`,
    },
    channel: {
      sql: `channel`,
      type: `string`,
      title: `Channel`,
    },
    saleDate: {
      sql: `sale_date`,
      type: `time`,
      title: `Sale Date`,
    },
  },
  
  dataSource: `default`,
});
