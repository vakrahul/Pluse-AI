cube('HospitalMaster', {
  sql: `SELECT * FROM dim.hospital_master`,

  joins: {
    TerritoryMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.territory_id = ${TerritoryMaster}.territory_id`,
    },
  },

  measures: {
    count: {
      type: 'count',
      description: 'Total number of hospitals',
    },
    totalBeds: {
      sql: 'bed_count',
      type: 'sum',
      description: 'Total bed count across hospitals',
    },
  },

  dimensions: {
    hospitalId: {
      sql: 'hospital_id',
      type: 'string',
      primaryKey: true,
    },
    hospitalName: {
      sql: 'hospital_name',
      type: 'string',
    },
    hospitalType: {
      sql: 'hospital_type',
      type: 'string',
    },
    city: {
      sql: 'city',
      type: 'string',
    },
    state: {
      sql: 'state',
      type: 'string',
    },
    territoryId: {
      sql: 'territory_id',
      type: 'string',
    },
  },
});
