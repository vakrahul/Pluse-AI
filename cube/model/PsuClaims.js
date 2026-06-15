cube(`PsuClaims`, {
  sql: `SELECT * FROM oasis_normalized.payer_360_psu_claims`,
  title: `PSU Claims`,
  description: `Patient Sub-Unit claims tracking actual patient counts per MCO and Brand`,

  measures: {
    count: {
      type: `count`,
      title: `Claim Count`,
    },
    totalPatientCount: {
      sql: `patient_count`,
      type: `sum`,
      title: `Total Patient Count`,
      description: `The actual number of patients tracked in these claims. Use this for market share.`,
    },
  },

  dimensions: {
    id: {
      sql: `psu_claim_id`,
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
    bookOfBusiness: {
      sql: `mdm_book_of_business`,
      type: `string`,
      title: `Book of Business`,
    },
    benefitType: {
      sql: `benefit_type`,
      type: `string`,
      title: `Benefit Type`,
    },
    claimStatus: {
      sql: `claim_status`,
      type: `string`,
      title: `Claim Status`,
    },
    claimDate: {
      sql: `claim_date`,
      type: `time`,
      title: `Claim Date`,
    },
  },
  
  dataSource: `default`,
});
