const http = require("http"); // http 모듈 불러오기
const url = "http://naver.com"; // 긁어오고 싶은 주소를 입력.

http.get(url, (stream) => {
  let rawdata = "";
  stream.setEncoding("utf8");
  stream.on("data", (buffer) => (rawdata += buffer));
  stream.on("end", function () {
    console.log(rawdata); // 긁어온 내용 뿌리기
  });
});
