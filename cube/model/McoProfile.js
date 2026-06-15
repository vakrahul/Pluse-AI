cube(`McoProfile`, {
  sql: `SELECT * FROM oasis_normalized.payer_360_master_mco_profile`,
  title: `MCO Profile`,
  description: `Managed Care Organization profiles — payer entities with hierarchy, book of business, and type`,

  measures: {
    count: {
      type: `count`,
      title: `Total MCOs`,
    },
    nationalCount: {
      type: `count`,
      filters: [{ sql: `${CUBE}.is_national = true` }],
      title: `National MCOs`,
    },
  },

  dimensions: {
    mcoId: {
      sql: `mdm_mco_id`,
      type: `string`,
      primaryKey: true,
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
      description: `Plan, PBM, Health System, IPA, GPO`,
    },
    bookOfBusiness: {
      sql: `mdm_book_of_business`,
      type: `string`,
      title: `Book of Business`,
      description: `Commercial, Medicare, Medicaid, Medicare_Advantage, Medicaid_Managed, Government`,
    },
    parentId: {
      sql: `mdm_parent_id`,
      type: `string`,
      title: `Parent MCO ID`,
    },
    isNational: {
      sql: `is_national`,
      type: `boolean`,
      title: `Is National`,
    },
    region: {
      sql: `region`,
      type: `string`,
      title: `Region`,
    },
    state: {
      sql: `state`,
      type: `string`,
      title: `State`,
    },
  },

  dataSource: `default`,
});
