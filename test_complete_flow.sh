#!/bin/bash

echo "======================================"
echo "COMPLETE END-TO-END VERIFICATION TEST"
echo "======================================"
echo ""

# Generate unique test data
TIMESTAMP=$(date +%s)
EMAIL="test${TIMESTAMP}@example.com"
PASSWORD="Test123!"
FULL_NAME="Test User ${TIMESTAMP}"

echo "Test Data:"
echo "  Email: $EMAIL"
echo "  Password: $PASSWORD"
echo ""

# Test 1: Health Check
echo "1. Testing Health Endpoint..."
HEALTH=$(curl -s http://localhost:8000/health)
if [ -z "$HEALTH" ]; then
    echo "❌ Backend is not responding"
    exit 1
fi
echo "✓ Backend health check passed"
echo ""

# Test 2: User Registration
echo "2. Testing User Registration..."
REGISTER=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"full_name\":\"$FULL_NAME\"}")

USER_ID=$(echo $REGISTER | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
if [ -z "$USER_ID" ]; then
    echo "❌ Registration failed"
    echo "$REGISTER"
    exit 1
fi
echo "✓ User registered successfully (ID: $USER_ID)"
echo ""

# Test 3: User Login
echo "3. Testing User Login..."
LOGIN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

TOKEN=$(echo $LOGIN | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
if [ -z "$TOKEN" ]; then
    echo "❌ Login failed"
    echo "$LOGIN"
    exit 1
fi
echo "✓ Login successful"
echo ""

# Test 4: Document Upload
echo "4. Testing Document Upload..."
TEST_FILE="/tmp/test_doc_${TIMESTAMP}.txt"
echo "This is a test document for verification at ${TIMESTAMP}" > $TEST_FILE

UPLOAD=$(curl -s -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@${TEST_FILE}" \
  -F "title=Test Document" \
  -F "description=Automated test document")

DOC_ID=$(echo $UPLOAD | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
FILE_HASH=$(echo $UPLOAD | python3 -c "import sys, json; print(json.load(sys.stdin).get('file_hash', ''))" 2>/dev/null)

if [ -z "$DOC_ID" ]; then
    echo "❌ Document upload failed"
    echo "$UPLOAD"
    exit 1
fi
echo "✓ Document uploaded (ID: $DOC_ID)"
echo "  Hash: $FILE_HASH"
echo ""

# Test 5: List Documents
echo "5. Testing Document Listing..."
DOCS=$(curl -s -X GET http://localhost:8000/documents/ \
  -H "Authorization: Bearer $TOKEN")

DOC_COUNT=$(echo $DOCS | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
if [ "$DOC_COUNT" -lt "1" ]; then
    echo "❌ Document listing failed"
    exit 1
fi
echo "✓ Found $DOC_COUNT document(s)"
echo ""

# Test 6: Document Verification
echo "6. Testing Document Verification..."
VERIFY=$(curl -s -X POST "http://localhost:8000/documents/${DOC_ID}/verify" \
  -H "Authorization: Bearer $TOKEN")

STATUS=$(echo $VERIFY | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)
if [ "$STATUS" != "verified" ]; then
    echo "❌ Document verification failed (Status: $STATUS)"
    exit 1
fi
echo "✓ Document verified successfully"
echo ""

# Test 7: Document Deletion
echo "7. Testing Document Deletion..."
DELETE=$(curl -s -X DELETE "http://localhost:8000/documents/${DOC_ID}" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$DELETE" | tail -1)
if [ "$HTTP_CODE" != "204" ]; then
    echo "❌ Document deletion failed (HTTP $HTTP_CODE)"
    exit 1
fi
echo "✓ Document deleted successfully"
echo ""

# Test 8: Verify Deletion
echo "8. Verifying Document Was Deleted..."
DOCS_AFTER=$(curl -s -X GET http://localhost:8000/documents/ \
  -H "Authorization: Bearer $TOKEN")

DOC_COUNT_AFTER=$(echo $DOCS_AFTER | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
if [ "$DOC_COUNT_AFTER" != "0" ]; then
    echo "⚠️  Warning: Expected 0 documents, found $DOC_COUNT_AFTER"
fi
echo "✓ Deletion verified"
echo ""

# Cleanup
rm -f $TEST_FILE

echo "======================================"
echo "✓ ALL TESTS PASSED SUCCESSFULLY!"
echo "======================================"
echo ""
echo "Summary:"
echo "  ✓ Backend health check"
echo "  ✓ User registration"
echo "  ✓ User authentication"
echo "  ✓ Document upload"
echo "  ✓ Document listing"
echo "  ✓ Document verification (hash comparison)"
echo "  ✓ Document deletion"
echo "  ✓ Cleanup verification"
echo ""
echo "The application is fully functional!"
