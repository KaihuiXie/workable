module.exports = {
  devServer: {
    proxy: {
      "/api": {
        target: "http://localhost:8080",
        ws: true,
        changOrigin: true,
        pathRewrite: {
          "^/api": "/",
          // http://localhost:8080/user/login
        },
      },
    },
  },
};
