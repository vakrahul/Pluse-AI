cube(`McoHierarchy`, {
  sql: `SELECT * FROM oasis_normalized.payer_360_mco_hierarchy`,
  title: `MCO Hierarchy`,
  description: `Parent-child MCO relationships with benefit type — use for payer hierarchy analysis`,

  measures: {
    count: {
      type: `count`,
      title: `Hierarchy Relationship Count`,
    },
    childCount: {
      type: `countDistinct`,
      sql: `mdm_child_id`,
      title: `Unique Child MCOs`,
    },
  },

  dimensions: {
    hashKey: {
      sql: `payer_360_hashkey`,
      type: `string`,
      primaryKey: true,
    },
    parentId: {
      sql: `mdm_parent_id`,
      type: `string`,
      title: `Parent MCO ID`,
    },
    parentName: {
      sql: `mdm_parent_name`,
      type: `string`,
      title: `Parent MCO Name`,
    },
    childId: {
      sql: `mdm_child_id`,
      type: `string`,
      title: `Child MCO ID`,
    },
    childName: {
      sql: `mdm_child_name`,
      type: `string`,
      title: `Child MCO Name`,
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
    benefitType: {
      sql: `benefit_type`,
      type: `string`,
      title: `Benefit Type`,
    },
  },

  dataSource: `default`,
});
