import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 5,
  duration: '10s',
};

export default function () {
  let res = http.get(`${__ENV.APP_URL}/`);
  check(res, {
    'status was 200': (r) => r.status == 200,
  });
}

