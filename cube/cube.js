module.exports = {
  schemaPath: 'model',
  telemetry: false,
  orchestratorOptions: {
    queryCacheOptions: {
      refreshKeyRenewalThreshold: 30,
      backgroundRenew: true,
    },
  },
};
