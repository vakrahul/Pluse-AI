cube(`Formulary`, {
  sql: `SELECT * FROM oasis_normalized.payer_360_formulary_rollup`,
  title: `Formulary & Access`,
  description: `Health Plan Management (HPM) values, formulary status, and access position per MCO x Brand x Date`,

  measures: {
    count: {
      type: `count`,
      title: `Formulary Record Count`,
    },
    advantageCount: {
      type: `count`,
      filters: [{ sql: `${CUBE}.access_position = 'Advantage'` }],
      title: `Advantage Count`,
    },
    parityCount: {
      type: `count`,
      filters: [{ sql: `${CUBE}.access_position = 'Parity'` }],
      title: `Parity Count`,
    },
    disadvantageCount: {
      type: `count`,
      filters: [{ sql: `${CUBE}.access_position = 'Disadvantage'` }],
      title: `Disadvantage Count`,
    },
  },

  dimensions: {
    hashKey: {
      sql: `payer_360_hashkey`,
      type: `string`,
      primaryKey: true,
    },
    mcoId: {
      sql: `mdm_mco_id`,
      type: `string`,
      title: `MCO ID`,
    },
    mcoName: {
      sql: `mdm_mco_name`,
      type: `string`,
      title: `MCO Name`,
    },
    mcoCategory: {
      sql: `mdm_mco_category`,
      type: `string`,
      title: `MCO Type`,
    },
    bookOfBusiness: {
      sql: `mdm_book_of_business`,
      type: `string`,
      title: `Book of Business`,
    },
    productBrandName: {
      sql: `product_brand_name`,
      type: `string`,
      title: `Brand`,
      description: `GNE brand name: Ocrevus, Xolair, Actemra, Vabysmo, Hemlibra etc.`,
    },
    hpmValue: {
      sql: `hpm_value`,
      type: `string`,
      title: `HPM Value`,
      description: `Preferred, Non-Preferred, PA Required, Step Edit, Not Covered, Specialty Tier`,
    },
    accessPosition: {
      sql: `access_position`,
      type: `string`,
      title: `Access Position`,
      description: `Advantage, Parity, or Disadvantage vs. competitor`,
    },
    formularyDate: {
      sql: `formulary_date`,
      type: `string`,
      title: `Formulary Date (YYYYMM)`,
    },
    benefitType: {
      sql: `benefit_type`,
      type: `string`,
      title: `Benefit Type`,
      description: `PHARMACY BENEFIT or MEDICAL BENEFIT`,
    },
  },

  dataSource: `default`,
});
