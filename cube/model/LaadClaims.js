cube(`LaadClaims`, {
  sql: `SELECT * FROM oasis_normalized.payer_360_laad_claims`,
  title: `LAAD Claims`,
  description: `Longitudinal Access and Adjudication Data`,

  measures: {
    count: {
      type: `count`,
      title: `Claim Count`,
    },
    totalOutOfPocket: {
      sql: `patient_out_of_pocket`,
      type: `sum`,
      title: `Total Patient OOP (USD)`,
    },
  },

  dimensions: {
    id: {
      sql: `laad_claim_id`,
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
    adjudicationStatus: {
      sql: `adjudication_status`,
      type: `string`,
      title: `Adjudication Status`,
    },
    claimDate: {
      sql: `claim_date`,
      type: `time`,
      title: `Claim Date`,
    },
  },
  
  dataSource: `default`,
});
