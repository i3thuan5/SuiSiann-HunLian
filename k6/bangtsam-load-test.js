import http from 'k6/http';
import { check } from 'k6';
import { SharedArray } from 'k6/data';
import exec from 'k6/execution';

const names = new SharedArray('taiwanese-names', function () {
  return JSON.parse(open('./data/taiwanese-names.json'));
});

export const options = {
  scenarios: {
    bangtsam: {
      executor: 'constant-arrival-rate',
      rate: 1,
      timeUnit: '1s',
      duration: '1m',
      preAllocatedVUs: 2,
      maxVUs: 10,
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.1'],
  },
};

export default function () {
  const idx = exec.scenario.iterationInTest % names.length;
  const entry = names[idx];
  const baseUrl = __ENV.BASE_URL || 'http://localhost:8000';
  const url = `${baseUrl}/bangtsam?taibun=${encodeURIComponent(entry.tailo)}`;

  const res = http.get(url, { timeout: '120s' });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'body is not empty': (r) => r.body && r.body.length > 0,
  });
}
