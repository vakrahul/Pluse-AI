cube('HcpMaster', {
  sql: `SELECT * FROM dim.hcp_master`,

  joins: {
    HospitalMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.hospital_id = ${HospitalMaster}.hospital_id`,
    },
    TerritoryMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.territory_id = ${TerritoryMaster}.territory_id`,
    },
  },

  measures: {
    count: {
      type: 'count',
      description: 'Total number of healthcare professionals',
    },
    avgSegmentationScore: {
      sql: 'segmentation_score',
      type: 'avg',
      description: 'Average HCP segmentation score (0-100)',
    },
    kolCount: {
      type: 'count',
      filters: [{ sql: `${CUBE}.is_kol = true` }],
      description: 'Count of Key Opinion Leaders',
    },
  },

  dimensions: {
    hcpId: {
      sql: 'hcp_id',
      type: 'string',
      primaryKey: true,
    },
    npiNumber: {
      sql: 'npi_number',
      type: 'string',
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
      description: 'HCP full name',
    },
    specialty: {
      sql: 'specialty',
      type: 'string',
      description: 'Medical specialty e.g. Cardiology',
    },
    subSpecialty: {
      sql: 'sub_specialty',
      type: 'string',
    },
    tier: {
      sql: 'tier',
      type: 'string',
      description: 'HCP tier: Gold, Silver, or Bronze',
    },
    segmentationScore: {
      sql: 'segmentation_score',
      type: 'number',
    },
    city: {
      sql: 'city',
      type: 'string',
    },
    state: {
      sql: 'state',
      type: 'string',
    },
    country: {
      sql: 'country',
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
    isKol: {
      sql: 'is_kol',
      type: 'boolean',
      description: 'Key Opinion Leader flag',
    },
    referralCount: {
      sql: 'referral_count',
      type: 'number',
    },
  },
});
