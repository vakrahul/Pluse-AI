cube('ProductMaster', {
  sql: `SELECT * FROM dim.product_master`,

  measures: {
    count: {
      type: 'count',
      description: 'Total number of products',
    },
    avgUnitPrice: {
      sql: 'unit_price',
      type: 'avg',
      description: 'Average unit price across products',
    },
  },

  dimensions: {
    productId: {
      sql: 'product_id',
      type: 'string',
      primaryKey: true,
    },
    productName: {
      sql: 'product_name',
      type: 'string',
      description: 'Product display name',
    },
    brandName: {
      sql: 'brand_name',
      type: 'string',
    },
    therapeuticArea: {
      sql: 'therapeutic_area',
      type: 'string',
      description: 'Therapeutic area e.g. Diabetes, Cardiology',
    },
    indication: {
      sql: 'indication',
      type: 'string',
    },
    molecule: {
      sql: 'molecule',
      type: 'string',
    },
    launchDate: {
      sql: 'launch_date',
      type: 'time',
    },
    isActive: {
      sql: 'is_active',
      type: 'boolean',
    },
  },
});
