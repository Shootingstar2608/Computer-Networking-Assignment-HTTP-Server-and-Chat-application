#!/bin/bash
# Test Task 1: HTTP Server với Cookie Session

echo "========================================="
echo "TEST TASK 1: HTTP Server với Cookie"
echo "========================================="
echo ""

URL="http://localhost:9000"

echo "=== Test 1A: POST /login với credentials HỢP LỆ ==="
echo "Request: POST /login với username=admin&password=password"
echo ""
curl -i -X POST "$URL/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"
echo ""
echo ""

echo "=== Test 1A: POST /login với credentials SAI ==="
echo "Request: POST /login với username=wrong&password=wrong"
echo ""
curl -i -X POST "$URL/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=wrong&password=wrong"
echo ""
echo ""

echo "=== Test 1B: GET / VỚI cookie auth=true ==="
echo "Request: GET / với Cookie: auth=true"
echo ""
curl -i "$URL/" -H "Cookie: auth=true"
echo ""
echo ""

echo "=== Test 1B: GET / KHÔNG CÓ cookie ==="
echo "Request: GET / không có Cookie"
echo ""
curl -i "$URL/"
echo ""
echo ""

echo "=== Test 1B: GET /index.html VỚI cookie ==="
echo "Request: GET /index.html với Cookie: auth=true"
echo ""
curl -i "$URL/index.html" -H "Cookie: auth=true"
echo ""
echo ""

echo "========================================="
echo "KẾT THÚC TEST"
echo "========================================="
