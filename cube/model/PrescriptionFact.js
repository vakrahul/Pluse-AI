cube('PrescriptionFact', {
  sql: `SELECT * FROM fact.prescription_fact`,

  joins: {
    HcpMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.hcp_id = ${HcpMaster}.hcp_id`,
    },
    ProductMaster: {
      relationship: 'many_to_one',
      sql: `${CUBE}.product_id = ${ProductMaster}.product_id`,
    },
  },

  measures: {
    count: {
      type: 'count',
      description: 'Number of prescription records',
    },
    prescriptionCount: {
      sql: 'rx_count',
      type: 'sum',
      description: 'Total prescriptions written. Business definition: sum of rx_count across all records.',
    },
    newPrescriptionCount: {
      sql: 'new_rx_count',
      type: 'sum',
      description: 'Total new prescriptions',
    },
    refillPrescriptionCount: {
      sql: 'refill_rx_count',
      type: 'sum',
      description: 'Total refill prescriptions',
    },
    patientCount: {
      sql: 'patient_count',
      type: 'sum',
      description: 'Total unique patients (aggregated)',
    },
  },

  dimensions: {
    rxId: {
      sql: 'rx_id',
      type: 'number',
      primaryKey: true,
    },
    rxDate: {
      sql: 'rx_date',
      type: 'time',
      description: 'Prescription date',
    },
    productId: {
      sql: 'product_id',
      type: 'string',
    },
    hcpId: {
      sql: 'hcp_id',
      type: 'string',
    },
  },
});
