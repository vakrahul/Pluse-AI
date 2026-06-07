cube('InteractionFact', {
  sql: `SELECT * FROM fact.interaction_fact`,

  joins: {
    HcpMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.hcp_id = ${HcpMaster}.hcp_id`,
    },
    SalesRepMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.rep_id = ${SalesRepMaster}.rep_id`,
    },
  },

  measures: {
    count: {
      type: 'count',
      description: 'Total number of rep-HCP interactions',
    },
    totalDurationMinutes: {
      sql: 'duration_minutes',
      type: 'sum',
      description: 'Total interaction duration in minutes',
    },
    avgDurationMinutes: {
      sql: 'duration_minutes',
      type: 'avg',
      description: 'Average interaction duration in minutes',
    },
    samplesProvided: {
      sql: 'samples_provided',
      type: 'sum',
      description: 'Total product samples provided',
    },
  },

  dimensions: {
    interactionId: {
      sql: 'interaction_id',
      type: 'number',
      primaryKey: true,
    },
    interactionDate: {
      sql: 'interaction_date',
      type: 'time',
      description: 'Date and time of interaction',
    },
    repId: {
      sql: 'rep_id',
      type: 'string',
    },
    hcpId: {
      sql: 'hcp_id',
      type: 'string',
    },
    interactionType: {
      sql: 'interaction_type',
      type: 'string',
      description: 'Visit, Call, Email, Webinar, Conference',
    },
    outcome: {
      sql: 'outcome',
      type: 'string',
    },
  },
});
