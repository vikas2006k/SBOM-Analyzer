# SBOM Analyzer API Specifications (Swagger Style)

This document provides detailed API specifications for the SBOM processing and Application Graph endpoints.

---

## 1. SBOM Management Module

### `POST /api/sbom/upload`
Upload JSON or CSV SBOM files.
*   **Authentication Required**: Yes (`Bearer <JWT_Token>`)
*   **Content-Type**: `multipart/form-data`
*   **Request Body**:
    *   `application_id` (integer, required): Target application ID profile.
    *   `file` (file, required): The target SBOM file binary (JSON or CSV). Max 25MB.
*   **Response (201 Created)**:
    ```json
    {
      "success": true,
      "message": "SBOM uploaded and staged successfully",
      "data": {
        "upload_id": 14,
        "file_name": "cyclonedx_production.json",
        "status": "PENDING",
        "checksum": "a8f7c9e0b1d2c3f4e5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8"
      }
    }
    ```
*   **Errors**:
    *   `400 Bad Request`: Missing `application_id`, invalid extension (only `.json`, `.csv` permitted), or duplicate upload match.
    *   `401 Unauthorized`: Missing or invalid bearer token.

---

### `POST /api/sbom/parse/{upload_id}`
Trigger validation and ingestion parser loop on a staged upload.
*   **Authentication Required**: Yes (`Bearer <JWT_Token>`)
*   **Path Parameters**:
    *   `upload_id` (integer, required): Staged upload ID key.
*   **Response (200 OK - Successful Ingestion)**:
    ```json
    {
      "success": true,
      "message": "SBOM parsed and ingested successfully",
      "data": {
        "status": "COMPLETED",
        "upload_id": 14,
        "libraries_imported": 42,
        "validation_report": {
          "valid": true,
          "errors": [],
          "warnings": [
            "Library 'log4j' has non-standard version formatting: '2.17.1-alpha'"
          ],
          "metrics": {
            "libraries_count": 42,
            "dependencies_count": 86,
            "has_cycles": false
          }
        }
      }
    }
    ```
*   **Response (400 Bad Request - Validation Failure)**:
    ```json
    {
      "success": false,
      "error": {
        "code": "BAD_REQUEST",
        "message": "SBOM validation failed",
        "details": {
          "status": "FAILED",
          "upload_id": 14,
          "errors": [
            "Circular dependency cycle detected: spring-boot-starter-web@3.1.2 -> jackson-databind@2.15.2 -> spring-boot-starter-web@3.1.2"
          ],
          "validation_report": {
            "valid": false,
            "errors": [
              "Circular dependency cycle detected: spring-boot-starter-web@3.1.2 -> jackson-databind@2.15.2 -> spring-boot-starter-web@3.1.2"
            ],
            "warnings": [],
            "metrics": {
              "libraries_count": 12,
              "dependencies_count": 14,
              "has_cycles": true
            }
          }
        }
      }
    }
    ```

---

### `GET /api/sbom/uploads`
List metadata records for all uploaded files.
*   **Authentication Required**: Yes (`Bearer <JWT_Token>`)
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "Uploads retrieved successfully",
      "data": [
        {
          "id": 14,
          "application_id": 2,
          "file_name": "cyclonedx_production.json",
          "file_format": "json",
          "status": "COMPLETED",
          "uploaded_by": 1,
          "created_at": "2026-07-11T12:00:00"
        }
      ]
    }
    ```

---

## 2. Applications Module

### `GET /api/applications/{app_id}`
Retrieve profile settings metadata for a registered application.
*   **Authentication Required**: Yes (`Bearer <JWT_Token>`)
*   **Path Parameters**:
    *   `app_id` (integer, required): Application ID key.
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "Application metadata retrieved successfully",
      "data": {
        "id": 2,
        "name": "PaymentGateway",
        "version": "1.0.0",
        "description": "Enterprise credit card billing and verification router",
        "business_criticality": "High",
        "created_at": "2026-07-11T10:00:00"
      }
    }
    ```

---

### `GET /api/applications/{app_id}/graph`
Get visual graph tree nodes and links formatted for React Flow display.
*   **Authentication Required**: Yes (`Bearer <JWT_Token>`)
*   **Path Parameters**:
    *   `app_id` (integer, required): Application ID key.
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "Adjacency matrix resolved successfully",
      "data": {
        "nodes": [
          {
            "id": "PaymentGateway@1.0.0",
            "type": "input",
            "data": {
              "label": "PaymentGateway v1.0.0",
              "name": "PaymentGateway",
              "version": "1.0.0",
              "depth": 0,
              "ecosystem": "application",
              "license": "Unknown"
            },
            "position": { "x": 0, "y": 0 }
          },
          {
            "id": "spring-boot-starter-web@3.1.2",
            "type": "customNode",
            "data": {
              "label": "spring-boot-starter-web v3.1.2",
              "name": "spring-boot-starter-web",
              "version": "3.1.2",
              "depth": 1,
              "ecosystem": "npm",
              "license": "Apache-2.0"
            },
            "position": { "x": 280, "y": 0 }
          }
        ],
        "edges": [
          {
            "id": "e-PaymentGateway@1.0.0-->spring-boot-starter-web@3.1.2",
            "source": "PaymentGateway@1.0.0",
            "target": "spring-boot-starter-web@3.1.2",
            "animated": true,
            "style": { "stroke": "#10b981" }
          }
        ],
        "metrics": {
          "nodes_count": 2,
          "edges_count": 1,
          "max_depth": 1
        }
      }
    }
    ```

---

### `GET /api/applications/{app_id}/dependencies`
List flat catalog of all direct and transitive dependency library items.
*   **Authentication Required**: Yes (`Bearer <JWT_Token>`)
*   **Path Parameters**:
    *   `app_id` (integer, required): Application ID key.
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "Application dependencies catalog retrieved successfully",
      "data": [
        {
          "id": 8,
          "name": "spring-boot-starter-web",
          "version": "3.1.2",
          "ecosystem": "npm",
          "license": "Apache-2.0",
          "depth": 1,
          "is_transitive": false
        },
        {
          "id": 9,
          "name": "jackson-databind",
          "version": "2.15.2",
          "ecosystem": "npm",
          "license": "Apache-2.0",
          "depth": 2,
          "is_transitive": true
        }
      ]
    }
    ```
