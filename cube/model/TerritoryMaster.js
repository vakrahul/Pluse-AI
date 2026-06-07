cube('TerritoryMaster', {
  sql: `SELECT * FROM dim.territory_master`,

  measures: {
    count: {
      type: 'count',
      description: 'Total number of territories',
    },
    salesTarget: {
      sql: 'sales_target',
      type: 'sum',
      description: 'Total sales target across territories',
    },
  },

  dimensions: {
    territoryId: {
      sql: 'territory_id',
      type: 'string',
      primaryKey: true,
    },
    territoryName: {
      sql: 'territory_name',
      type: 'string',
      description: 'Territory display name',
    },
    region: {
      sql: 'region',
      type: 'string',
    },
    zone: {
      sql: 'zone',
      type: 'string',
    },
    country: {
      sql: 'country',
      type: 'string',
    },
  },
});
