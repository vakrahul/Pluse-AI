cube('SalesRepMaster', {
  sql: `SELECT * FROM dim.sales_rep_master`,

  joins: {
    TerritoryMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.territory_id = ${TerritoryMaster}.territory_id`,
    },
  },

  measures: {
    count: {
      type: 'count',
      description: 'Total number of sales reps',
    },
  },

  dimensions: {
    repId: {
      sql: 'rep_id',
      type: 'string',
      primaryKey: true,
    },
    firstName: {
      sql: 'first_name',
      type: 'string',
    },
    lastName: {
      sql: 'last_name',
      type: 'string',
    },
    fullName: {
      sql: `CONCAT(first_name, ' ', last_name)`,
      type: 'string',
      description: 'Sales rep full name',
    },
    email: {
      sql: 'email',
      type: 'string',
    },
    territoryId: {
      sql: 'territory_id',
      type: 'string',
    },
    isActive: {
      sql: 'is_active',
      type: 'boolean',
    },
  },
});
