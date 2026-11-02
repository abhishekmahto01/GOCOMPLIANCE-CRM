--
-- PostgreSQL database dump
--

\restrict tkBFkfoUwUaTXrvUXh0Tdh5KJkQ6AWUzVOFZWEhTah0ztY7D0n2hXLEKvXAACXK

-- Dumped from database version 18.4 (Homebrew)
-- Dumped by pg_dump version 18.4 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accounts_audit_log; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.accounts_audit_log (
    audit_id uuid NOT NULL,
    company_id uuid NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id uuid NOT NULL,
    action character varying(50) NOT NULL,
    actor_user_id uuid NOT NULL,
    old_values text,
    new_values text,
    reason character varying(500),
    ip_address character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.accounts_audit_log OWNER TO abhishekmahto;

--
-- Name: TABLE accounts_audit_log; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.accounts_audit_log IS 'Immutable financial audit logs for Accounts module';


--
-- Name: accounts_expense; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.accounts_expense (
    expense_id uuid NOT NULL,
    company_id uuid NOT NULL,
    sales_order_id uuid,
    expense_number character varying(50) NOT NULL,
    category character varying(50) NOT NULL,
    amount numeric(12,2) NOT NULL,
    expense_date date NOT NULL,
    payee_name character varying(200) NOT NULL,
    paid_by_type character varying(30) DEFAULT 'COMPANY'::character varying NOT NULL,
    paid_by_user_id uuid,
    payment_mode character varying(50) DEFAULT 'BANK_TRANSFER'::character varying NOT NULL,
    transaction_reference character varying(100),
    bill_attachment_path character varying(500),
    bill_attachment_name character varying(255),
    remark character varying(1000),
    approval_status character varying(30) DEFAULT 'PENDING_APPROVAL'::character varying NOT NULL,
    approved_by_user_id uuid,
    approved_at timestamp with time zone,
    rejection_reason character varying(500),
    settlement_status character varying(30) DEFAULT 'NOT_APPLICABLE'::character varying NOT NULL,
    settled_at timestamp with time zone,
    settled_by_user_id uuid,
    settlement_reference character varying(100),
    created_by_user_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.accounts_expense OWNER TO abhishekmahto;

--
-- Name: TABLE accounts_expense; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.accounts_expense IS 'Direct costs and employee reimbursements ledger for Accounts module';


--
-- Name: accounts_follow_up; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.accounts_follow_up (
    follow_up_id uuid NOT NULL,
    company_id uuid NOT NULL,
    sales_order_id uuid NOT NULL,
    follow_up_date date NOT NULL,
    next_follow_up_date date,
    contact_channel character varying(50) DEFAULT 'PHONE'::character varying NOT NULL,
    contact_person character varying(150),
    remark_text character varying(1000) NOT NULL,
    created_by_user_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.accounts_follow_up OWNER TO abhishekmahto;

--
-- Name: TABLE accounts_follow_up; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.accounts_follow_up IS 'Follow-up history and debtor remarks for Accounts module';


--
-- Name: accounts_invoice; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.accounts_invoice (
    invoice_id uuid NOT NULL,
    company_id uuid NOT NULL,
    sales_order_id uuid NOT NULL,
    invoice_type character varying(30) NOT NULL,
    invoice_number character varying(100) NOT NULL,
    invoice_date date NOT NULL,
    due_date date,
    amount numeric(12,2) NOT NULL,
    taxable_amount numeric(12,2),
    cgst_amount numeric(12,2),
    sgst_amount numeric(12,2),
    igst_amount numeric(12,2),
    status character varying(30) DEFAULT 'ISSUED'::character varying NOT NULL,
    file_path character varying(500),
    file_name character varying(255),
    notes character varying(1000),
    created_by_user_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.accounts_invoice OWNER TO abhishekmahto;

--
-- Name: TABLE accounts_invoice; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.accounts_invoice IS 'Invoice metadata and document attachments for Accounts module';


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO abhishekmahto;

--
-- Name: application_activity_log; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.application_activity_log (
    activity_id uuid NOT NULL,
    application_id uuid NOT NULL,
    actor_user_id uuid NOT NULL,
    action_type character varying(50) NOT NULL,
    old_value character varying(255),
    new_value character varying(255),
    comment character varying(1000),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.application_activity_log OWNER TO abhishekmahto;

--
-- Name: TABLE application_activity_log; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.application_activity_log IS 'Timeline and audit log of status changes and operational activities';


--
-- Name: COLUMN application_activity_log.activity_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_activity_log.activity_id IS 'Unique identifier for the activity log entry (UUIDv4)';


--
-- Name: COLUMN application_activity_log.application_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_activity_log.application_id IS 'Foreign key referencing operation_application.application_id (ON DELETE CASCADE)';


--
-- Name: COLUMN application_activity_log.actor_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_activity_log.actor_user_id IS 'User who triggered this operational action';


--
-- Name: COLUMN application_activity_log.action_type; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_activity_log.action_type IS 'Action classification: STATUS_CHANGE, DOCUMENT_STATUS_CHANGE, PRIORITY_CHANGE, DUE_DATE_CHANGE, NOTE_ADDED, ASSIGNMENT_CHANGE';


--
-- Name: COLUMN application_activity_log.old_value; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_activity_log.old_value IS 'Previous attribute value prior to modification';


--
-- Name: COLUMN application_activity_log.new_value; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_activity_log.new_value IS 'New attribute value after modification';


--
-- Name: COLUMN application_activity_log.comment; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_activity_log.comment IS 'Descriptive note or reason accompanying the activity';


--
-- Name: COLUMN application_activity_log.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_activity_log.created_at IS 'Timestamp when activity occurred (UTC)';


--
-- Name: application_assignment_history; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.application_assignment_history (
    history_id uuid NOT NULL,
    application_id uuid NOT NULL,
    assigned_by_user_id uuid NOT NULL,
    previous_assignee_user_id uuid,
    new_assignee_user_id uuid,
    reason character varying(500),
    assigned_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.application_assignment_history OWNER TO abhishekmahto;

--
-- Name: TABLE application_assignment_history; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.application_assignment_history IS 'Audit trail for application assignment and reassignment events';


--
-- Name: COLUMN application_assignment_history.history_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_assignment_history.history_id IS 'Unique identifier for the assignment history record (UUIDv4)';


--
-- Name: COLUMN application_assignment_history.application_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_assignment_history.application_id IS 'Foreign key referencing operation_application.application_id (ON DELETE CASCADE)';


--
-- Name: COLUMN application_assignment_history.assigned_by_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_assignment_history.assigned_by_user_id IS 'Manager/Admin who performed the assignment';


--
-- Name: COLUMN application_assignment_history.previous_assignee_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_assignment_history.previous_assignee_user_id IS 'Employee previously assigned (null if initial assignment)';


--
-- Name: COLUMN application_assignment_history.new_assignee_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_assignment_history.new_assignee_user_id IS 'Employee newly assigned (null if unassigned)';


--
-- Name: COLUMN application_assignment_history.reason; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_assignment_history.reason IS 'Reason or notes provided for assignment/reassignment';


--
-- Name: COLUMN application_assignment_history.assigned_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_assignment_history.assigned_at IS 'Timestamp when assignment was executed (UTC)';


--
-- Name: application_document; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.application_document (
    app_doc_id uuid NOT NULL,
    application_id uuid NOT NULL,
    document_code character varying(60) NOT NULL,
    document_name character varying(150) NOT NULL,
    is_mandatory boolean DEFAULT true NOT NULL,
    status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    rejection_reason character varying(500),
    verified_by_user_id uuid,
    verified_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_app_doc_status_valid CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'RECEIVED'::character varying, 'VERIFIED'::character varying, 'REJECTED'::character varying, 'NOT_APPLICABLE'::character varying])::text[])))
);


ALTER TABLE public.application_document OWNER TO abhishekmahto;

--
-- Name: TABLE application_document; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.application_document IS 'Document requirements and verification statuses for an active application';


--
-- Name: COLUMN application_document.app_doc_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_document.app_doc_id IS 'Unique identifier for the application document requirement (UUIDv4)';


--
-- Name: COLUMN application_document.application_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_document.application_id IS 'Foreign key referencing operation_application.application_id (ON DELETE CASCADE)';


--
-- Name: COLUMN application_document.document_code; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_document.document_code IS 'Document identifier code (e.g. AADHAAR, PAN, RENT_AGREEMENT)';


--
-- Name: COLUMN application_document.document_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_document.document_name IS 'Human-readable document name';


--
-- Name: COLUMN application_document.is_mandatory; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_document.is_mandatory IS 'Whether this document is required for filing';


--
-- Name: COLUMN application_document.status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_document.status IS 'Document status: PENDING, RECEIVED, VERIFIED, REJECTED, NOT_APPLICABLE';


--
-- Name: COLUMN application_document.rejection_reason; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_document.rejection_reason IS 'Reason if document was rejected / defective';


--
-- Name: COLUMN application_document.verified_by_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_document.verified_by_user_id IS 'Employee who verified/approved the document';


--
-- Name: COLUMN application_document.verified_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_document.verified_at IS 'Timestamp when document was verified';


--
-- Name: COLUMN application_document.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_document.created_at IS 'Timestamp when document item was created (UTC)';


--
-- Name: COLUMN application_document.updated_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.application_document.updated_at IS 'Timestamp when document item was last updated (UTC)';


--
-- Name: auth_refresh_token; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.auth_refresh_token (
    refresh_token_id uuid NOT NULL,
    user_id uuid NOT NULL,
    jti character varying(64) NOT NULL,
    token_hash character varying(128) NOT NULL,
    issued_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    revoked_at timestamp with time zone,
    replaced_by_jti character varying(64),
    created_ip character varying(45),
    user_agent character varying(500)
);


ALTER TABLE public.auth_refresh_token OWNER TO abhishekmahto;

--
-- Name: TABLE auth_refresh_token; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.auth_refresh_token IS 'Registry for hashed rotating refresh tokens and session revocation';


--
-- Name: COLUMN auth_refresh_token.refresh_token_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.auth_refresh_token.refresh_token_id IS 'Unique identifier for the refresh token record (UUIDv4)';


--
-- Name: COLUMN auth_refresh_token.user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.auth_refresh_token.user_id IS 'Foreign key referencing user_master.user_id (ON DELETE CASCADE)';


--
-- Name: COLUMN auth_refresh_token.jti; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.auth_refresh_token.jti IS 'Unique JWT identifier (JTI) of the refresh token';


--
-- Name: COLUMN auth_refresh_token.token_hash; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.auth_refresh_token.token_hash IS 'Cryptographic SHA-256 hash of the issued refresh token (raw token is never stored)';


--
-- Name: COLUMN auth_refresh_token.issued_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.auth_refresh_token.issued_at IS 'Timestamp when the refresh token was issued (UTC)';


--
-- Name: COLUMN auth_refresh_token.expires_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.auth_refresh_token.expires_at IS 'Expiration timestamp for the refresh token (UTC)';


--
-- Name: COLUMN auth_refresh_token.revoked_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.auth_refresh_token.revoked_at IS 'Timestamp when the token was explicitly revoked/logged out/rotated (UTC)';


--
-- Name: COLUMN auth_refresh_token.replaced_by_jti; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.auth_refresh_token.replaced_by_jti IS 'JTI of the replacement refresh token upon rotation (for reuse detection)';


--
-- Name: COLUMN auth_refresh_token.created_ip; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.auth_refresh_token.created_ip IS 'Client IP address that requested the token';


--
-- Name: COLUMN auth_refresh_token.user_agent; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.auth_refresh_token.user_agent IS 'Client user agent string';


--
-- Name: client_master; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.client_master (
    client_id uuid NOT NULL,
    company_id uuid NOT NULL,
    client_name character varying(200) NOT NULL,
    entity_type character varying(50) DEFAULT 'INDIVIDUAL'::character varying NOT NULL,
    contact_person character varying(150) DEFAULT ''::character varying NOT NULL,
    contact_email character varying(255) DEFAULT ''::character varying,
    contact_phone character varying(20) NOT NULL,
    pan_number character varying(20),
    gstin character varying(20),
    city character varying(100),
    state character varying(100),
    created_by_user_id uuid NOT NULL,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_client_status_valid CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'INACTIVE'::character varying])::text[])))
);


ALTER TABLE public.client_master OWNER TO abhishekmahto;

--
-- Name: TABLE client_master; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.client_master IS 'Master registry for corporate and individual clients in Gocompliances CRM';


--
-- Name: COLUMN client_master.client_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.client_id IS 'Unique identifier for the client (UUIDv4)';


--
-- Name: COLUMN client_master.company_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.company_id IS 'Foreign key referencing company_master.company_id (ON DELETE RESTRICT)';


--
-- Name: COLUMN client_master.client_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.client_name IS 'Business or individual trade name (e.g. Sharma Enterprises, Gupta Traders)';


--
-- Name: COLUMN client_master.entity_type; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.entity_type IS 'Entity type: Private Limited, LLP, One Person Company, Partnership, Proprietorship, Individual';


--
-- Name: COLUMN client_master.contact_person; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.contact_person IS 'Primary contact person name';


--
-- Name: COLUMN client_master.contact_email; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.contact_email IS 'Primary contact email address';


--
-- Name: COLUMN client_master.contact_phone; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.contact_phone IS 'Primary contact phone / mobile number';


--
-- Name: COLUMN client_master.pan_number; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.pan_number IS 'Income Tax PAN number of the client entity';


--
-- Name: COLUMN client_master.gstin; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.gstin IS 'GST Identification Number (GSTIN) if applicable';


--
-- Name: COLUMN client_master.city; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.city IS 'Operating city';


--
-- Name: COLUMN client_master.state; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.state IS 'Operating state / union territory';


--
-- Name: COLUMN client_master.created_by_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.created_by_user_id IS 'Foreign key referencing user who onboarded this client';


--
-- Name: COLUMN client_master.status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.status IS 'Operational status: ACTIVE or INACTIVE';


--
-- Name: COLUMN client_master.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.created_at IS 'Timestamp when client record was created (UTC)';


--
-- Name: COLUMN client_master.updated_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.client_master.updated_at IS 'Timestamp when client record was last updated (UTC)';


--
-- Name: company_master; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.company_master (
    company_id uuid NOT NULL,
    company_code character varying(20) NOT NULL,
    company_name character varying(150) NOT NULL,
    legal_name character varying(200),
    employee_code_prefix character varying(5) NOT NULL,
    next_employee_number integer DEFAULT 1 NOT NULL,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_company_employee_code_prefix_format CHECK (((employee_code_prefix)::text ~ '^[A-Z]{2,5}$'::text)),
    CONSTRAINT chk_company_next_employee_number_positive CHECK ((next_employee_number > 0)),
    CONSTRAINT chk_company_status_valid CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'INACTIVE'::character varying])::text[])))
);


ALTER TABLE public.company_master OWNER TO abhishekmahto;

--
-- Name: TABLE company_master; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.company_master IS 'Master registry for companies operating within Gocompliances CRM';


--
-- Name: COLUMN company_master.company_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.company_master.company_id IS 'Unique identifier for the company (UUIDv4)';


--
-- Name: COLUMN company_master.company_code; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.company_master.company_code IS 'Unique uppercase business identifier code (e.g., GOCOMPLIANCES)';


--
-- Name: COLUMN company_master.company_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.company_master.company_name IS 'Primary trade/display name of the company';


--
-- Name: COLUMN company_master.legal_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.company_master.legal_name IS 'Registered legal/corporate entity name (optional)';


--
-- Name: COLUMN company_master.employee_code_prefix; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.company_master.employee_code_prefix IS '2-5 character uppercase prefix for employee IDs (e.g. CG, EP, BM)';


--
-- Name: COLUMN company_master.next_employee_number; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.company_master.next_employee_number IS 'Sequential counter for next employee code assignment (>0)';


--
-- Name: COLUMN company_master.status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.company_master.status IS 'Operational status: ACTIVE or INACTIVE';


--
-- Name: COLUMN company_master.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.company_master.created_at IS 'Timestamp when company record was created (UTC)';


--
-- Name: COLUMN company_master.updated_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.company_master.updated_at IS 'Timestamp when company record was last updated (UTC)';


--
-- Name: department_master; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.department_master (
    department_id uuid NOT NULL,
    department_code character varying(30) NOT NULL,
    department_name character varying(100) NOT NULL,
    description character varying(500),
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_department_code_format CHECK (((department_code)::text ~ '^[A-Z_]+$'::text)),
    CONSTRAINT chk_department_status_valid CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'INACTIVE'::character varying])::text[])))
);


ALTER TABLE public.department_master OWNER TO abhishekmahto;

--
-- Name: TABLE department_master; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.department_master IS 'Master registry for company-specific departments in Gocompliances CRM';


--
-- Name: COLUMN department_master.department_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.department_master.department_id IS 'Unique identifier for the department (UUIDv4)';


--
-- Name: COLUMN department_master.department_code; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.department_master.department_code IS 'Uppercase department code unique per company (e.g., ADMINISTRATION, SALES)';


--
-- Name: COLUMN department_master.department_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.department_master.department_name IS 'Display name of the department (e.g., Administration, Sales, R&D)';


--
-- Name: COLUMN department_master.description; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.department_master.description IS 'Optional description of the department functions';


--
-- Name: COLUMN department_master.status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.department_master.status IS 'Operational status: ACTIVE or INACTIVE';


--
-- Name: COLUMN department_master.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.department_master.created_at IS 'Timestamp when department record was created (UTC)';


--
-- Name: COLUMN department_master.updated_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.department_master.updated_at IS 'Timestamp when department record was last updated (UTC)';


--
-- Name: designation_master; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.designation_master (
    designation_id uuid NOT NULL,
    designation_code character varying(50) NOT NULL,
    designation_name character varying(100) NOT NULL,
    level_rank integer NOT NULL,
    is_managerial boolean DEFAULT false NOT NULL,
    description character varying(500),
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_designation_code_format CHECK (((designation_code)::text ~ '^[A-Z_]+$'::text)),
    CONSTRAINT chk_designation_level_rank_positive CHECK ((level_rank > 0)),
    CONSTRAINT chk_designation_status_valid CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'INACTIVE'::character varying])::text[])))
);


ALTER TABLE public.designation_master OWNER TO abhishekmahto;

--
-- Name: TABLE designation_master; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.designation_master IS 'Master registry for company-specific employee designations in Gocompliances CRM';


--
-- Name: COLUMN designation_master.designation_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.designation_master.designation_id IS 'Unique identifier for the designation (UUIDv4)';


--
-- Name: COLUMN designation_master.designation_code; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.designation_master.designation_code IS 'Uppercase designation code unique per company (e.g., EXECUTIVE, MANAGER)';


--
-- Name: COLUMN designation_master.designation_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.designation_master.designation_name IS 'Display job title of the designation (e.g., Executive, Manager, Director)';


--
-- Name: COLUMN designation_master.level_rank; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.designation_master.level_rank IS 'Seniority level ranking counter (>0; higher value = higher seniority)';


--
-- Name: COLUMN designation_master.is_managerial; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.designation_master.is_managerial IS 'Classification flag indicating managerial position (informational only; does not grant permissions)';


--
-- Name: COLUMN designation_master.description; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.designation_master.description IS 'Optional description of the designation responsibilities';


--
-- Name: COLUMN designation_master.status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.designation_master.status IS 'Operational status: ACTIVE or INACTIVE';


--
-- Name: COLUMN designation_master.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.designation_master.created_at IS 'Timestamp when designation record was created (UTC)';


--
-- Name: COLUMN designation_master.updated_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.designation_master.updated_at IS 'Timestamp when designation record was last updated (UTC)';


--
-- Name: impersonation_audit_logs; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.impersonation_audit_logs (
    audit_id uuid NOT NULL,
    session_id uuid,
    actor_admin_id uuid,
    target_user_id uuid NOT NULL,
    action character varying(50) NOT NULL,
    details jsonb,
    ip_address character varying(50),
    user_agent character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.impersonation_audit_logs OWNER TO abhishekmahto;

--
-- Name: TABLE impersonation_audit_logs; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.impersonation_audit_logs IS 'Immutable audit log of impersonation starts, exits, and actions';


--
-- Name: impersonation_sessions; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.impersonation_sessions (
    session_id uuid NOT NULL,
    actor_admin_id uuid NOT NULL,
    target_user_id uuid NOT NULL,
    impersonation_token_jti character varying(64) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    ended_at timestamp with time zone,
    ended_reason character varying(50),
    created_ip character varying(50),
    user_agent character varying(255)
);


ALTER TABLE public.impersonation_sessions OWNER TO abhishekmahto;

--
-- Name: TABLE impersonation_sessions; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.impersonation_sessions IS 'Registry of Super Admin employee impersonation sessions';


--
-- Name: module_master; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.module_master (
    module_id uuid NOT NULL,
    module_code character varying(60) NOT NULL,
    module_name character varying(100) NOT NULL,
    parent_module_id uuid,
    route character varying(200),
    description character varying(500),
    display_order integer DEFAULT 0 NOT NULL,
    is_navigation boolean DEFAULT true NOT NULL,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_module_code_format CHECK (((module_code)::text ~ '^[A-Z_]+$'::text)),
    CONSTRAINT chk_module_display_order_non_negative CHECK ((display_order >= 0)),
    CONSTRAINT chk_module_route_format CHECK (((route IS NULL) OR ((route)::text ~ '^/'::text))),
    CONSTRAINT chk_module_self_parent CHECK (((parent_module_id IS NULL) OR (parent_module_id <> module_id))),
    CONSTRAINT chk_module_status_valid CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'INACTIVE'::character varying])::text[])))
);


ALTER TABLE public.module_master OWNER TO abhishekmahto;

--
-- Name: TABLE module_master; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.module_master IS 'Master registry for application modules, sub-modules and navigation hierarchy';


--
-- Name: COLUMN module_master.module_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.module_master.module_id IS 'Unique identifier for the module (UUIDv4)';


--
-- Name: COLUMN module_master.module_code; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.module_master.module_code IS 'Uppercase unique system identifier (e.g., ADMIN, ADMIN_COMPANIES)';


--
-- Name: COLUMN module_master.module_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.module_master.module_name IS 'Display name of the module (e.g., Admin, Companies, Sales)';


--
-- Name: COLUMN module_master.parent_module_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.module_master.parent_module_id IS 'Nullable self-referencing foreign key to parent module (ON DELETE RESTRICT)';


--
-- Name: COLUMN module_master.route; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.module_master.route IS 'Frontend route path starting with ''/'' (unique if provided)';


--
-- Name: COLUMN module_master.description; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.module_master.description IS 'Optional description of module features';


--
-- Name: COLUMN module_master.display_order; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.module_master.display_order IS 'Display sorting order (>= 0; lower value = higher priority)';


--
-- Name: COLUMN module_master.is_navigation; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.module_master.is_navigation IS 'Whether module should appear in UI navigation (does not grant permission)';


--
-- Name: COLUMN module_master.status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.module_master.status IS 'Operational status: ACTIVE or INACTIVE';


--
-- Name: COLUMN module_master.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.module_master.created_at IS 'Timestamp when module record was created (UTC)';


--
-- Name: COLUMN module_master.updated_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.module_master.updated_at IS 'Timestamp when module record was last updated (UTC)';


--
-- Name: operation_application; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.operation_application (
    application_id uuid NOT NULL,
    application_number character varying(30) NOT NULL,
    sales_order_id uuid NOT NULL,
    company_id uuid NOT NULL,
    client_id uuid NOT NULL,
    service_id uuid NOT NULL,
    assigned_to_user_id uuid,
    assigned_by_user_id uuid,
    assigned_at timestamp with time zone,
    priority character varying(10) DEFAULT 'MEDIUM'::character varying NOT NULL,
    application_status character varying(30) DEFAULT 'UNASSIGNED'::character varying NOT NULL,
    target_due_date date,
    completion_date date,
    assignment_notes character varying(1000),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason character varying(1000),
    CONSTRAINT chk_op_application_priority_valid CHECK (((priority)::text = ANY ((ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'URGENT'::character varying])::text[]))),
    CONSTRAINT chk_op_application_status_valid CHECK (((application_status)::text = ANY ((ARRAY['UNASSIGNED'::character varying, 'ASSIGNED'::character varying, 'IN_PROGRESS'::character varying, 'PENDING_DOCUMENTS'::character varying, 'READY_FOR_SUBMISSION'::character varying, 'SUBMITTED'::character varying, 'AUTHORITY_QUERY'::character varying, 'APPROVED'::character varying, 'CANCELLED'::character varying])::text[])))
);


ALTER TABLE public.operation_application OWNER TO abhishekmahto;

--
-- Name: TABLE operation_application; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.operation_application IS 'Operations workflow application tracking statutory filings and task fulfillment';


--
-- Name: COLUMN operation_application.application_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.application_id IS 'Unique identifier for the operation application (UUIDv4)';


--
-- Name: COLUMN operation_application.application_number; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.application_number IS 'Unique formatted application code (e.g. AP-2025-0084)';


--
-- Name: COLUMN operation_application.sales_order_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.sales_order_id IS '1-to-1 foreign key to originating sales order (strictly idempotent)';


--
-- Name: COLUMN operation_application.company_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.company_id IS 'Foreign key referencing company_master.company_id';


--
-- Name: COLUMN operation_application.client_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.client_id IS 'Foreign key referencing client_master.client_id';


--
-- Name: COLUMN operation_application.service_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.service_id IS 'Foreign key referencing service_master.service_id';


--
-- Name: COLUMN operation_application.assigned_to_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.assigned_to_user_id IS 'Operations employee currently assigned to this task (nullable when UNASSIGNED)';


--
-- Name: COLUMN operation_application.assigned_by_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.assigned_by_user_id IS 'Operations Manager / Admin who assigned or reassigned this task';


--
-- Name: COLUMN operation_application.assigned_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.assigned_at IS 'Timestamp when task was assigned to current employee';


--
-- Name: COLUMN operation_application.priority; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.priority IS 'Task priority: LOW, MEDIUM, HIGH, URGENT';


--
-- Name: COLUMN operation_application.application_status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.application_status IS 'Lifecycle status: UNASSIGNED, ASSIGNED, IN_PROGRESS, PENDING_DOCUMENTS, READY_FOR_SUBMISSION, SUBMITTED, AUTHORITY_QUERY, APPROVED, CANCELLED';


--
-- Name: COLUMN operation_application.target_due_date; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.target_due_date IS 'Target completion due date for statutory filing';


--
-- Name: COLUMN operation_application.completion_date; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.completion_date IS 'Actual completion / approval date';


--
-- Name: COLUMN operation_application.assignment_notes; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.assignment_notes IS 'Internal handover or assignment instructions';


--
-- Name: COLUMN operation_application.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.created_at IS 'Timestamp when application record was created (UTC)';


--
-- Name: COLUMN operation_application.updated_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.updated_at IS 'Timestamp when application record was last updated (UTC)';


--
-- Name: COLUMN operation_application.deleted_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.deleted_at IS 'Timestamp when linked sales order was soft-deleted (UTC)';


--
-- Name: COLUMN operation_application.deleted_by; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.deleted_by IS 'Foreign key referencing user who soft-deleted the linked sales order';


--
-- Name: COLUMN operation_application.deletion_reason; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_application.deletion_reason IS 'Required or provided deletion justification reason';


--
-- Name: operation_remark; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.operation_remark (
    remark_id uuid NOT NULL,
    application_id uuid NOT NULL,
    author_user_id uuid NOT NULL,
    remark_text character varying(2000) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.operation_remark OWNER TO abhishekmahto;

--
-- Name: TABLE operation_remark; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.operation_remark IS 'Operations remarks history tracking reasons for delays, blockers, or progress context';


--
-- Name: COLUMN operation_remark.remark_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_remark.remark_id IS 'Unique identifier for the operation remark (UUIDv4)';


--
-- Name: COLUMN operation_remark.application_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_remark.application_id IS 'Foreign key referencing operation_application.application_id (ON DELETE CASCADE)';


--
-- Name: COLUMN operation_remark.author_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_remark.author_user_id IS 'User who authored this operation remark';


--
-- Name: COLUMN operation_remark.remark_text; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_remark.remark_text IS 'Remark explanation or status update text';


--
-- Name: COLUMN operation_remark.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.operation_remark.created_at IS 'Timestamp when remark was recorded (UTC)';


--
-- Name: operations_coordinator_config; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.operations_coordinator_config (
    config_id uuid NOT NULL,
    company_id uuid NOT NULL,
    coordinator_user_id uuid,
    updated_by_user_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.operations_coordinator_config OWNER TO abhishekmahto;

--
-- Name: TABLE operations_coordinator_config; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.operations_coordinator_config IS 'Configuration mapping Sales entry company to default Operations coordinator';


--
-- Name: payment_transaction; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.payment_transaction (
    payment_id uuid NOT NULL,
    company_id uuid NOT NULL,
    sales_order_id uuid NOT NULL,
    payment_number character varying(50) NOT NULL,
    amount numeric(12,2) NOT NULL,
    payment_date date NOT NULL,
    payment_mode character varying(50) DEFAULT 'BANK_TRANSFER'::character varying NOT NULL,
    transaction_reference character varying(100),
    receiving_account character varying(100),
    proof_attachment_path character varying(500),
    proof_attachment_name character varying(255),
    remark character varying(1000),
    submitted_by_user_id uuid NOT NULL,
    submitted_at timestamp with time zone DEFAULT now() NOT NULL,
    verification_status character varying(30) DEFAULT 'PENDING_VERIFICATION'::character varying NOT NULL,
    verified_by_user_id uuid,
    verified_at timestamp with time zone,
    reversal_reason character varying(500),
    reversed_by_user_id uuid,
    reversed_at timestamp with time zone,
    is_opening_balance boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.payment_transaction OWNER TO abhishekmahto;

--
-- Name: TABLE payment_transaction; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.payment_transaction IS 'Payment receipts and collections ledger for Accounts module';


--
-- Name: permission_audit_log; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.permission_audit_log (
    audit_id uuid NOT NULL,
    actor_user_id uuid,
    target_user_id uuid NOT NULL,
    action_type character varying(50) NOT NULL,
    before_state jsonb,
    after_state jsonb NOT NULL,
    ip_address character varying(50),
    user_agent character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.permission_audit_log OWNER TO abhishekmahto;

--
-- Name: TABLE permission_audit_log; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.permission_audit_log IS 'Immutable audit trail for permission changes and user access modifications';


--
-- Name: COLUMN permission_audit_log.audit_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.permission_audit_log.audit_id IS 'Unique identifier for the audit log entry (UUIDv4)';


--
-- Name: COLUMN permission_audit_log.actor_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.permission_audit_log.actor_user_id IS 'User ID of the administrator/user performing the action (ON DELETE SET NULL)';


--
-- Name: COLUMN permission_audit_log.target_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.permission_audit_log.target_user_id IS 'User ID of the employee whose permissions were modified (ON DELETE CASCADE)';


--
-- Name: COLUMN permission_audit_log.action_type; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.permission_audit_log.action_type IS 'Audit action type: PERMISSION_UPDATE, PERMISSION_COPY, USER_SETTINGS_UPDATE';


--
-- Name: COLUMN permission_audit_log.before_state; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.permission_audit_log.before_state IS 'State of permissions/settings prior to modification';


--
-- Name: COLUMN permission_audit_log.after_state; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.permission_audit_log.after_state IS 'State of permissions/settings after modification';


--
-- Name: COLUMN permission_audit_log.ip_address; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.permission_audit_log.ip_address IS 'IP address of the client that triggered the action';


--
-- Name: COLUMN permission_audit_log.user_agent; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.permission_audit_log.user_agent IS 'User agent header from client request';


--
-- Name: COLUMN permission_audit_log.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.permission_audit_log.created_at IS 'Timestamp when the change was executed (UTC)';


--
-- Name: sales_order; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.sales_order (
    order_id uuid NOT NULL,
    order_number character varying(30) NOT NULL,
    company_id uuid NOT NULL,
    client_id uuid NOT NULL,
    service_id uuid NOT NULL,
    salesperson_user_id uuid NOT NULL,
    lead_source character varying(50) DEFAULT 'DIRECT'::character varying NOT NULL,
    order_date date NOT NULL,
    order_value numeric(12,2) NOT NULL,
    amount_received numeric(12,2) DEFAULT 0.00 NOT NULL,
    balance_amount numeric(12,2) DEFAULT 0.00 NOT NULL,
    payment_status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    confirmation_status character varying(20) DEFAULT 'DRAFT'::character varying NOT NULL,
    confirmed_at timestamp with time zone,
    notes character varying(1000),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    proforma_invoice_no character varying(100),
    tax_invoice_no character varying(100),
    reimbursement_note character varying(500),
    govt_fees numeric(12,2) DEFAULT 0.00 NOT NULL,
    incidental_cost numeric(12,2) DEFAULT 0.00 NOT NULL,
    profit_amount numeric(12,2) DEFAULT 0.00 NOT NULL,
    location character varying(200),
    gst_invoice_required boolean DEFAULT false NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason character varying(1000),
    CONSTRAINT chk_sales_order_advance_le_total CHECK ((amount_received <= order_value)),
    CONSTRAINT chk_sales_order_balance_non_negative CHECK ((balance_amount >= (0)::numeric)),
    CONSTRAINT chk_sales_order_confirmation_status_valid CHECK (((confirmation_status)::text = ANY ((ARRAY['DRAFT'::character varying, 'CONFIRMED'::character varying, 'CANCELLED'::character varying])::text[]))),
    CONSTRAINT chk_sales_order_govt_fees_non_negative CHECK ((govt_fees >= (0)::numeric)),
    CONSTRAINT chk_sales_order_incidental_cost_non_negative CHECK ((incidental_cost >= (0)::numeric)),
    CONSTRAINT chk_sales_order_payment_status_valid CHECK (((payment_status)::text = ANY ((ARRAY['FULLY_PAID'::character varying, 'PARTIALLY_PAID'::character varying, 'PENDING'::character varying, 'OVERDUE'::character varying])::text[]))),
    CONSTRAINT chk_sales_order_received_non_negative CHECK ((amount_received >= (0)::numeric)),
    CONSTRAINT chk_sales_order_value_non_negative CHECK ((order_value >= (0)::numeric))
);


ALTER TABLE public.sales_order OWNER TO abhishekmahto;

--
-- Name: TABLE sales_order; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.sales_order IS 'Master registry for client sales orders and collection tracking';


--
-- Name: COLUMN sales_order.order_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.order_id IS 'Unique identifier for the sales order (UUIDv4)';


--
-- Name: COLUMN sales_order.order_number; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.order_number IS 'Unique formatted order code (e.g. SO-2025-0048)';


--
-- Name: COLUMN sales_order.company_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.company_id IS 'Foreign key referencing company_master.company_id';


--
-- Name: COLUMN sales_order.client_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.client_id IS 'Foreign key referencing client_master.client_id';


--
-- Name: COLUMN sales_order.service_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.service_id IS 'Foreign key referencing service_master.service_id';


--
-- Name: COLUMN sales_order.salesperson_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.salesperson_user_id IS 'Foreign key referencing sales employee who closed the order';


--
-- Name: COLUMN sales_order.lead_source; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.lead_source IS 'Lead acquisition channel: WEBSITE, REFERRAL, DIRECT, OTHERS';


--
-- Name: COLUMN sales_order.order_date; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.order_date IS 'Date when order was placed';


--
-- Name: COLUMN sales_order.order_value; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.order_value IS 'Total order contract value in INR';


--
-- Name: COLUMN sales_order.amount_received; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.amount_received IS 'Total amount collected/received in INR';


--
-- Name: COLUMN sales_order.balance_amount; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.balance_amount IS 'Outstanding balance amount in INR (order_value - amount_received)';


--
-- Name: COLUMN sales_order.payment_status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.payment_status IS 'Payment collection status: FULLY_PAID, PARTIALLY_PAID, PENDING, OVERDUE';


--
-- Name: COLUMN sales_order.confirmation_status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.confirmation_status IS 'Order confirmation workflow state: DRAFT, CONFIRMED, CANCELLED';


--
-- Name: COLUMN sales_order.confirmed_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.confirmed_at IS 'Timestamp when order was confirmed and handed over to operations';


--
-- Name: COLUMN sales_order.notes; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.notes IS 'Order notes or instructions from sales team';


--
-- Name: COLUMN sales_order.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.created_at IS 'Timestamp when order record was created (UTC)';


--
-- Name: COLUMN sales_order.updated_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.updated_at IS 'Timestamp when order record was last updated (UTC)';


--
-- Name: COLUMN sales_order.proforma_invoice_no; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.proforma_invoice_no IS 'Proforma invoice reference code';


--
-- Name: COLUMN sales_order.tax_invoice_no; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.tax_invoice_no IS 'Final tax invoice reference code';


--
-- Name: COLUMN sales_order.reimbursement_note; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.reimbursement_note IS 'Reimbursement note or expense instructions';


--
-- Name: COLUMN sales_order.govt_fees; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.govt_fees IS 'Government statutory / filing fees in INR';


--
-- Name: COLUMN sales_order.incidental_cost; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.incidental_cost IS 'Incidental / operational expenses in INR';


--
-- Name: COLUMN sales_order.profit_amount; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.profit_amount IS 'Net profit in INR (order_value - govt_fees - incidental_cost)';


--
-- Name: COLUMN sales_order.location; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.location IS 'Branch / City / Work location for multi-location clients';


--
-- Name: COLUMN sales_order.gst_invoice_required; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.gst_invoice_required IS 'Routing flag: True if GST invoice is required and should appear in Accounts';


--
-- Name: COLUMN sales_order.deleted_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.deleted_at IS 'Timestamp when sales order was soft-deleted (UTC)';


--
-- Name: COLUMN sales_order.deleted_by; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.deleted_by IS 'Foreign key referencing user who soft-deleted the order';


--
-- Name: COLUMN sales_order.deletion_reason; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.sales_order.deletion_reason IS 'Required or provided deletion justification reason';


--
-- Name: sales_order_audit_log; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.sales_order_audit_log (
    audit_id uuid NOT NULL,
    sales_order_id uuid NOT NULL,
    actor_user_id uuid NOT NULL,
    action_type character varying(50) NOT NULL,
    linked_task_id uuid,
    previous_status character varying(100),
    deletion_reason character varying(1000),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.sales_order_audit_log OWNER TO abhishekmahto;

--
-- Name: service_master; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.service_master (
    service_id uuid NOT NULL,
    service_code character varying(60) NOT NULL,
    service_name character varying(150) NOT NULL,
    category character varying(50) NOT NULL,
    description character varying(500),
    base_price numeric(12,2) DEFAULT 0.00 NOT NULL,
    govt_fee numeric(12,2) DEFAULT 0.00 NOT NULL,
    standard_turnaround_days integer DEFAULT 15 NOT NULL,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_service_base_price_non_negative CHECK ((base_price >= (0)::numeric)),
    CONSTRAINT chk_service_code_format CHECK (((service_code)::text ~ '^[A-Z0-9_]+$'::text)),
    CONSTRAINT chk_service_govt_fee_non_negative CHECK ((govt_fee >= (0)::numeric)),
    CONSTRAINT chk_service_status_valid CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'INACTIVE'::character varying])::text[]))),
    CONSTRAINT chk_service_turnaround_positive CHECK ((standard_turnaround_days > 0))
);


ALTER TABLE public.service_master OWNER TO abhishekmahto;

--
-- Name: TABLE service_master; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.service_master IS 'Master registry for compliance services, licences, and statutory filings';


--
-- Name: COLUMN service_master.service_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_master.service_id IS 'Unique identifier for the service (UUIDv4)';


--
-- Name: COLUMN service_master.service_code; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_master.service_code IS 'Uppercase unique system identifier (e.g. TRADE_LICENSE, SHOP_ACT, CLRA)';


--
-- Name: COLUMN service_master.service_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_master.service_name IS 'Display name of the service/licence (e.g. Trade License, Shop Act)';


--
-- Name: COLUMN service_master.category; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_master.category IS 'Service classification: LICENCE, REGISTRATION, INCORPORATION, COMPLIANCE';


--
-- Name: COLUMN service_master.description; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_master.description IS 'Optional service description and statutory scope';


--
-- Name: COLUMN service_master.base_price; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_master.base_price IS 'Standard professional fee / base price in INR';


--
-- Name: COLUMN service_master.govt_fee; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_master.govt_fee IS 'Estimated government statutory fee in INR';


--
-- Name: COLUMN service_master.standard_turnaround_days; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_master.standard_turnaround_days IS 'Standard estimated SLA turnaround time in days';


--
-- Name: COLUMN service_master.status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_master.status IS 'Operational status: ACTIVE or INACTIVE';


--
-- Name: COLUMN service_master.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_master.created_at IS 'Timestamp when service record was created (UTC)';


--
-- Name: COLUMN service_master.updated_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_master.updated_at IS 'Timestamp when service record was last updated (UTC)';


--
-- Name: service_required_document; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.service_required_document (
    doc_config_id uuid NOT NULL,
    service_id uuid NOT NULL,
    document_code character varying(60) NOT NULL,
    document_name character varying(150) NOT NULL,
    is_mandatory boolean DEFAULT true NOT NULL,
    display_order integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_service_doc_display_order_non_negative CHECK ((display_order >= 0))
);


ALTER TABLE public.service_required_document OWNER TO abhishekmahto;

--
-- Name: TABLE service_required_document; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.service_required_document IS 'Standard document checklist configuration required for each service';


--
-- Name: COLUMN service_required_document.doc_config_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_required_document.doc_config_id IS 'Unique identifier for the document requirement configuration (UUIDv4)';


--
-- Name: COLUMN service_required_document.service_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_required_document.service_id IS 'Foreign key referencing service_master.service_id (ON DELETE CASCADE)';


--
-- Name: COLUMN service_required_document.document_code; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_required_document.document_code IS 'System code for document (e.g. AADHAAR, PAN, RENT_AGREEMENT, PROPERTY_TAX)';


--
-- Name: COLUMN service_required_document.document_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_required_document.document_name IS 'Human-readable document name (e.g. Aadhaar Card of Applicant)';


--
-- Name: COLUMN service_required_document.is_mandatory; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_required_document.is_mandatory IS 'Whether this document is mandatory for application submission';


--
-- Name: COLUMN service_required_document.display_order; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_required_document.display_order IS 'Display sorting order in document checklists';


--
-- Name: COLUMN service_required_document.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_required_document.created_at IS 'Timestamp when document configuration was created (UTC)';


--
-- Name: COLUMN service_required_document.updated_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.service_required_document.updated_at IS 'Timestamp when document configuration was last updated (UTC)';


--
-- Name: source_master; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.source_master (
    source_id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_code character varying(50) NOT NULL,
    source_name character varying(100) NOT NULL,
    description text,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    is_system boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_source_code_format CHECK (((source_code)::text ~ '^[A-Z0-9_]+$'::text)),
    CONSTRAINT chk_source_status_valid CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'INACTIVE'::character varying])::text[])))
);


ALTER TABLE public.source_master OWNER TO abhishekmahto;

--
-- Name: TABLE source_master; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.source_master IS 'Master registry for lead acquisition sources and marketing channels';


--
-- Name: COLUMN source_master.source_code; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.source_master.source_code IS 'Uppercase unique identifier for source, e.g. WEBSITE, JUSTDIAL';


--
-- Name: COLUMN source_master.source_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.source_master.source_name IS 'Display name for source, e.g. Website, Justdial, IndiaMART';


--
-- Name: COLUMN source_master.description; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.source_master.description IS 'Optional description of the acquisition source';


--
-- Name: COLUMN source_master.status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.source_master.status IS 'ACTIVE or INACTIVE';


--
-- Name: COLUMN source_master.is_system; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.source_master.is_system IS 'Flag indicating system-seeded default source';


--
-- Name: task_conversation_message; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.task_conversation_message (
    message_id uuid NOT NULL,
    sales_order_id uuid NOT NULL,
    author_user_id uuid,
    message_type character varying(30) DEFAULT 'COMMENT'::character varying NOT NULL,
    message_text text NOT NULL,
    author_name character varying(150) DEFAULT 'System'::character varying NOT NULL,
    author_employee_code character varying(30),
    author_department_name character varying(100),
    author_role_name character varying(100),
    event_type character varying(50),
    event_metadata text,
    idempotency_key character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    originating_module character varying(30),
    CONSTRAINT chk_task_conv_msg_type_valid CHECK (((message_type)::text = ANY ((ARRAY['COMMENT'::character varying, 'SYSTEM_EVENT'::character varying])::text[])))
);


ALTER TABLE public.task_conversation_message OWNER TO abhishekmahto;

--
-- Name: TABLE task_conversation_message; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.task_conversation_message IS 'Unified append-only conversation timeline across Sales, Operations, and Accounts';


--
-- Name: task_conversation_read_state; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.task_conversation_read_state (
    read_id uuid NOT NULL,
    message_id uuid NOT NULL,
    user_id uuid NOT NULL,
    sales_order_id uuid NOT NULL,
    read_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.task_conversation_read_state OWNER TO abhishekmahto;

--
-- Name: TABLE task_conversation_read_state; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.task_conversation_read_state IS 'Per-user independent read receipt tracking for shared task conversations';


--
-- Name: user_master; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.user_master (
    user_id uuid NOT NULL,
    employee_code character varying(20) NOT NULL,
    company_id uuid NOT NULL,
    department_id uuid NOT NULL,
    designation_id uuid NOT NULL,
    manager_user_id uuid,
    first_name character varying(100) NOT NULL,
    middle_name character varying(100),
    last_name character varying(100) NOT NULL,
    official_email character varying(255) NOT NULL,
    personal_email character varying(255),
    mobile_number character varying(20) NOT NULL,
    date_of_joining date NOT NULL,
    employment_type character varying(20) NOT NULL,
    account_status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    password_hash character varying(255),
    must_change_password boolean DEFAULT true NOT NULL,
    failed_login_attempts integer DEFAULT 0 NOT NULL,
    locked_until timestamp with time zone,
    last_login_at timestamp with time zone,
    password_changed_at timestamp with time zone,
    token_version integer DEFAULT 1 NOT NULL,
    credentials_initialized_at timestamp with time zone,
    is_hod boolean DEFAULT false NOT NULL,
    is_reporting_manager boolean DEFAULT false NOT NULL,
    primary_location character varying(100),
    CONSTRAINT chk_user_account_status_valid CHECK (((account_status)::text = ANY ((ARRAY['PENDING'::character varying, 'ACTIVE'::character varying, 'INACTIVE'::character varying, 'SUSPENDED'::character varying])::text[]))),
    CONSTRAINT chk_user_employment_type_valid CHECK (((employment_type)::text = ANY ((ARRAY['FULL_TIME'::character varying, 'PART_TIME'::character varying, 'CONTRACT'::character varying, 'INTERN'::character varying, 'CONSULTANT'::character varying])::text[]))),
    CONSTRAINT chk_user_failed_login_attempts_non_negative CHECK ((failed_login_attempts >= 0)),
    CONSTRAINT chk_user_self_manager CHECK (((manager_user_id IS NULL) OR (manager_user_id <> user_id))),
    CONSTRAINT chk_user_token_version_positive CHECK ((token_version > 0))
);


ALTER TABLE public.user_master OWNER TO abhishekmahto;

--
-- Name: TABLE user_master; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.user_master IS 'Master registry for employees/users in Gocompliances CRM';


--
-- Name: COLUMN user_master.user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.user_id IS 'Unique identifier for the user / employee (UUIDv4)';


--
-- Name: COLUMN user_master.employee_code; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.employee_code IS 'Globally unique uppercase employee code (e.g. CG0001, EP0001, BM0001)';


--
-- Name: COLUMN user_master.company_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.company_id IS 'Foreign key referencing company_master.company_id (ON DELETE RESTRICT)';


--
-- Name: COLUMN user_master.department_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.department_id IS 'Foreign key referencing department_master.department_id (ON DELETE RESTRICT)';


--
-- Name: COLUMN user_master.designation_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.designation_id IS 'Foreign key referencing designation_master.designation_id (ON DELETE RESTRICT)';


--
-- Name: COLUMN user_master.manager_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.manager_user_id IS 'Nullable self-referencing foreign key to reporting manager (ON DELETE SET NULL)';


--
-- Name: COLUMN user_master.first_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.first_name IS 'Employee first name';


--
-- Name: COLUMN user_master.middle_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.middle_name IS 'Employee middle name (optional)';


--
-- Name: COLUMN user_master.last_name; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.last_name IS 'Employee last name';


--
-- Name: COLUMN user_master.official_email; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.official_email IS 'Official corporate email address (case-insensitively unique)';


--
-- Name: COLUMN user_master.personal_email; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.personal_email IS 'Personal email address (optional)';


--
-- Name: COLUMN user_master.mobile_number; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.mobile_number IS 'Primary contact mobile number (e.g. +91XXXXXXXXXX)';


--
-- Name: COLUMN user_master.date_of_joining; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.date_of_joining IS 'Official date of joining';


--
-- Name: COLUMN user_master.employment_type; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.employment_type IS 'Employment type: FULL_TIME, PART_TIME, CONTRACT, INTERN, CONSULTANT';


--
-- Name: COLUMN user_master.account_status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.account_status IS 'Account/employment status: PENDING, ACTIVE, INACTIVE, SUSPENDED';


--
-- Name: COLUMN user_master.created_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.created_at IS 'Timestamp when user record was created (UTC)';


--
-- Name: COLUMN user_master.updated_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.updated_at IS 'Timestamp when user record was last updated (UTC)';


--
-- Name: COLUMN user_master.password_hash; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.password_hash IS 'Argon2id password hash (nullable until user activates account)';


--
-- Name: COLUMN user_master.must_change_password; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.must_change_password IS 'Flag indicating if password change is required on next login';


--
-- Name: COLUMN user_master.failed_login_attempts; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.failed_login_attempts IS 'Counter for consecutive failed login attempts';


--
-- Name: COLUMN user_master.locked_until; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.locked_until IS 'Timestamp until which account is locked due to failed login attempts';


--
-- Name: COLUMN user_master.last_login_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.last_login_at IS 'Timestamp of most recent successful login (UTC)';


--
-- Name: COLUMN user_master.password_changed_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.password_changed_at IS 'Timestamp when password was last changed (UTC)';


--
-- Name: COLUMN user_master.token_version; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.token_version IS 'Session token version for global revocation';


--
-- Name: COLUMN user_master.credentials_initialized_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.credentials_initialized_at IS 'Timestamp when credentials were first provisioned (UTC)';


--
-- Name: COLUMN user_master.is_hod; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.is_hod IS 'Whether user is designated as Head of Department (HOD)';


--
-- Name: COLUMN user_master.is_reporting_manager; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.is_reporting_manager IS 'Whether user is designated as a Reporting Manager';


--
-- Name: COLUMN user_master.primary_location; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_master.primary_location IS 'Primary operating location / branch of the employee';


--
-- Name: user_module_permission; Type: TABLE; Schema: public; Owner: abhishekmahto
--

CREATE TABLE public.user_module_permission (
    permission_id uuid NOT NULL,
    user_id uuid NOT NULL,
    module_id uuid NOT NULL,
    can_view boolean DEFAULT false NOT NULL,
    can_create boolean DEFAULT false NOT NULL,
    can_edit boolean DEFAULT false NOT NULL,
    can_delete boolean DEFAULT false NOT NULL,
    can_approve boolean DEFAULT false NOT NULL,
    data_scope character varying(20) DEFAULT 'SELF'::character varying NOT NULL,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    granted_by_user_id uuid,
    granted_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    can_assign boolean DEFAULT false NOT NULL,
    can_reassign boolean DEFAULT false NOT NULL,
    can_export boolean DEFAULT false NOT NULL,
    CONSTRAINT chk_permission_action_requires_view CHECK (((can_view = true) OR ((can_create = false) AND (can_edit = false) AND (can_delete = false) AND (can_approve = false) AND (can_assign = false) AND (can_reassign = false) AND (can_export = false)))),
    CONSTRAINT chk_permission_data_scope_valid CHECK (((data_scope)::text = ANY ((ARRAY['SELF'::character varying, 'TEAM'::character varying, 'DEPARTMENT'::character varying, 'COMPANY'::character varying, 'ALL'::character varying])::text[]))),
    CONSTRAINT chk_permission_expires_after_granted CHECK (((expires_at IS NULL) OR (expires_at > granted_at))),
    CONSTRAINT chk_permission_status_valid CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'INACTIVE'::character varying])::text[])))
);


ALTER TABLE public.user_module_permission OWNER TO abhishekmahto;

--
-- Name: TABLE user_module_permission; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON TABLE public.user_module_permission IS 'Per-user granular permissions and data scope assignments for CRM modules';


--
-- Name: COLUMN user_module_permission.permission_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.permission_id IS 'Unique identifier for the permission grant (UUIDv4)';


--
-- Name: COLUMN user_module_permission.user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.user_id IS 'Foreign key referencing target user (ON DELETE CASCADE)';


--
-- Name: COLUMN user_module_permission.module_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.module_id IS 'Foreign key referencing target module (ON DELETE RESTRICT)';


--
-- Name: COLUMN user_module_permission.can_view; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.can_view IS 'Permission to view module page and query records within data scope';


--
-- Name: COLUMN user_module_permission.can_create; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.can_create IS 'Permission to create new records in module (requires can_view=true)';


--
-- Name: COLUMN user_module_permission.can_edit; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.can_edit IS 'Permission to edit records in module (requires can_view=true)';


--
-- Name: COLUMN user_module_permission.can_delete; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.can_delete IS 'Permission to delete/deactivate records in module (requires can_view=true)';


--
-- Name: COLUMN user_module_permission.can_approve; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.can_approve IS 'Permission to execute approval workflows in module (requires can_view=true)';


--
-- Name: COLUMN user_module_permission.data_scope; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.data_scope IS 'Data visibility scope: SELF, TEAM, DEPARTMENT, COMPANY, ALL';


--
-- Name: COLUMN user_module_permission.status; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.status IS 'Permission status: ACTIVE or INACTIVE';


--
-- Name: COLUMN user_module_permission.granted_by_user_id; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.granted_by_user_id IS 'Nullable foreign key to grantor user (ON DELETE SET NULL)';


--
-- Name: COLUMN user_module_permission.granted_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.granted_at IS 'Timestamp when permission was granted (UTC)';


--
-- Name: COLUMN user_module_permission.expires_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.expires_at IS 'Optional expiration timestamp for temporary access (UTC)';


--
-- Name: COLUMN user_module_permission.updated_at; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.updated_at IS 'Timestamp when permission record was last updated (UTC)';


--
-- Name: COLUMN user_module_permission.can_assign; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.can_assign IS 'Permission to assign orders/tasks in module (requires can_view=true)';


--
-- Name: COLUMN user_module_permission.can_reassign; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.can_reassign IS 'Permission to reassign orders/tasks in module (requires can_view=true)';


--
-- Name: COLUMN user_module_permission.can_export; Type: COMMENT; Schema: public; Owner: abhishekmahto
--

COMMENT ON COLUMN public.user_module_permission.can_export IS 'Permission to export reports/records in module (requires can_view=true)';


--
-- Data for Name: accounts_audit_log; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.accounts_audit_log (audit_id, company_id, entity_type, entity_id, action, actor_user_id, old_values, new_values, reason, ip_address, created_at) FROM stdin;
2c472c3b-a024-43f5-94af-b9878b8f4a1f	5242338c-3887-56db-b86c-c59deae26654	SALES_ORDER	9f937f0a-66bf-4635-ba53-739203287a4c	ACCOUNTS_UPDATE	de526836-5e73-49d7-9be3-8ad07caa6090	{"proforma_invoice_no": null, "tax_invoice_no": null, "reimbursement_note": null, "notes": null}	{"proforma_invoice_no": "sfvklflvdmfvlkmd"}	Updated Accounts financial fields	\N	2026-10-07 00:25:40.599272+05:30
3fec4639-5666-44f2-ba4d-0530399a31d3	5242338c-3887-56db-b86c-c59deae26654	SALES_ORDER	9f937f0a-66bf-4635-ba53-739203287a4c	ACCOUNTS_UPDATE	de526836-5e73-49d7-9be3-8ad07caa6090	{"proforma_invoice_no": "sfvklflvdmfvlkmd", "tax_invoice_no": null, "reimbursement_note": null, "notes": null}	{"tax_invoice_no": "dfm ,fd. dnlkdfn"}	Updated Accounts financial fields	\N	2026-10-07 00:25:45.311003+05:30
8c12c087-e789-4536-a139-fc86960caca0	5242338c-3887-56db-b86c-c59deae26654	SALES_ORDER	9f937f0a-66bf-4635-ba53-739203287a4c	ACCOUNTS_UPDATE	de526836-5e73-49d7-9be3-8ad07caa6090	{"proforma_invoice_no": "sfvklflvdmfvlkmd", "tax_invoice_no": "dfm ,fd. dnlkdfn", "reimbursement_note": null, "notes": null}	{"reimbursement_note": "df vnf mv"}	Updated Accounts financial fields	\N	2026-10-07 00:25:49.615932+05:30
086221a2-5103-41cf-85af-8849e617ed13	5242338c-3887-56db-b86c-c59deae26654	SALES_ORDER	9f937f0a-66bf-4635-ba53-739203287a4c	ACCOUNTS_UPDATE	de526836-5e73-49d7-9be3-8ad07caa6090	{"proforma_invoice_no": "sfvklflvdmfvlkmd", "tax_invoice_no": "dfm ,fd. dnlkdfn", "reimbursement_note": "df vnf mv", "notes": null}	{"notes": "vdfb kjgfd"}	Updated Accounts financial fields	\N	2026-10-07 00:25:55.000529+05:30
faf34da3-6c0d-4628-bb17-64595925636a	5242338c-3887-56db-b86c-c59deae26654	SALES_ORDER	7558b3f8-00f9-4897-a5b2-5d01f137555c	ACCOUNTS_UPDATE	de526836-5e73-49d7-9be3-8ad07caa6090	{"proforma_invoice_no": null, "tax_invoice_no": null, "reimbursement_note": null, "notes": null}	{"notes": "hello hunny bunny"}	Updated Accounts financial fields	\N	2026-10-07 01:34:16.352271+05:30
644367c6-02c3-4dc7-a876-00cbac7dc07a	5242338c-3887-56db-b86c-c59deae26654	SALES_ORDER	c3f09177-7fc9-436b-bdd5-d177c419d38e	ACCOUNTS_UPDATE	de526836-5e73-49d7-9be3-8ad07caa6090	{"proforma_invoice_no": null, "tax_invoice_no": null, "reimbursement_note": null, "notes": null}	{"proforma_invoice_no": "ybyugf6gt"}	Updated Accounts financial fields	\N	2026-10-07 16:09:59.535368+05:30
c52d82b4-e5a2-442b-af62-5eff6d8ce5e6	5242338c-3887-56db-b86c-c59deae26654	SALES_ORDER	c3f09177-7fc9-436b-bdd5-d177c419d38e	ACCOUNTS_UPDATE	de526836-5e73-49d7-9be3-8ad07caa6090	{"proforma_invoice_no": "ybyugf6gt", "tax_invoice_no": null, "reimbursement_note": null, "notes": null}	{"tax_invoice_no": "vtcfr5"}	Updated Accounts financial fields	\N	2026-10-07 16:10:04.821307+05:30
d9739e8c-7c21-42be-bec4-2748672f1f5b	5242338c-3887-56db-b86c-c59deae26654	SALES_ORDER	c3f09177-7fc9-436b-bdd5-d177c419d38e	ACCOUNTS_UPDATE	de526836-5e73-49d7-9be3-8ad07caa6090	{"proforma_invoice_no": "ybyugf6gt", "tax_invoice_no": "vtcfr5", "reimbursement_note": null, "notes": null}	{"reimbursement_note": "vftcvt"}	Updated Accounts financial fields	\N	2026-10-07 16:10:10.70416+05:30
704bc985-d186-49e6-a608-b24a72b135d4	5242338c-3887-56db-b86c-c59deae26654	SALES_ORDER	ce897913-8de9-422d-8d1f-f415cf3504a7	ACCOUNTS_UPDATE	de526836-5e73-49d7-9be3-8ad07caa6090	{"proforma_invoice_no": null, "tax_invoice_no": null, "reimbursement_note": null, "notes": "CALL AKASH 456789"}	{"proforma_invoice_no": "24562772"}	Updated Accounts financial fields	\N	2026-10-09 19:52:24.810051+05:30
3166c019-7cea-4545-9fbf-a0e3d6c930e4	5242338c-3887-56db-b86c-c59deae26654	SALES_ORDER	ce897913-8de9-422d-8d1f-f415cf3504a7	ACCOUNTS_UPDATE	de526836-5e73-49d7-9be3-8ad07caa6090	{"proforma_invoice_no": "24562772", "tax_invoice_no": null, "reimbursement_note": null, "notes": "CALL AKASH 456789"}	{"tax_invoice_no": "63782882"}	Updated Accounts financial fields	\N	2026-10-09 19:54:38.61077+05:30
25d4c540-0d01-4386-91d0-a2dd5c9e9654	5242338c-3887-56db-b86c-c59deae26654	SALES_ORDER	ce897913-8de9-422d-8d1f-f415cf3504a7	ACCOUNTS_UPDATE	de526836-5e73-49d7-9be3-8ad07caa6090	{"proforma_invoice_no": "24562772", "tax_invoice_no": "63782882", "reimbursement_note": null, "notes": "CALL AKASH 456789"}	{"reimbursement_note": "2672377823"}	Updated Accounts financial fields	\N	2026-10-09 19:54:42.815809+05:30
\.


--
-- Data for Name: accounts_expense; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.accounts_expense (expense_id, company_id, sales_order_id, expense_number, category, amount, expense_date, payee_name, paid_by_type, paid_by_user_id, payment_mode, transaction_reference, bill_attachment_path, bill_attachment_name, remark, approval_status, approved_by_user_id, approved_at, rejection_reason, settlement_status, settled_at, settled_by_user_id, settlement_reference, created_by_user_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: accounts_follow_up; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.accounts_follow_up (follow_up_id, company_id, sales_order_id, follow_up_date, next_follow_up_date, contact_channel, contact_person, remark_text, created_by_user_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: accounts_invoice; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.accounts_invoice (invoice_id, company_id, sales_order_id, invoice_type, invoice_number, invoice_date, due_date, amount, taxable_amount, cgst_amount, sgst_amount, igst_amount, status, file_path, file_name, notes, created_by_user_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.alembic_version (version_num) FROM stdin;
f7b8c9d0e1f2
\.


--
-- Data for Name: application_activity_log; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.application_activity_log (activity_id, application_id, actor_user_id, action_type, old_value, new_value, comment, created_at) FROM stdin;
de983cd4-f49e-495d-898e-0353a56b5e0e	e1770a62-2997-4d34-9258-9300d62d5cbf	de526836-5e73-49d7-9be3-8ad07caa6090	STATUS_CHANGE	NONE	UNASSIGNED	Order 'SO-2026-0001' confirmed and handed over from Sales.	2026-09-23 23:42:54.314988+05:30
d3801cea-280e-467e-a8ea-57e66bc88819	3ca55838-d953-4175-a37a-780ff438c869	de526836-5e73-49d7-9be3-8ad07caa6090	STATUS_CHANGE	NONE	UNASSIGNED	Order 'SO-2026-0002' confirmed and handed over from Sales.	2026-09-24 00:04:08.416007+05:30
c04babe0-99eb-4c45-ab97-c13af84b67e2	3ca55838-d953-4175-a37a-780ff438c869	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	UNASSIGNED	Mansi Singhal (CG0003)	Assigned to Mansi Singhal. Priority: MEDIUM	2026-09-24 00:04:08.416007+05:30
ffa5e082-c3fd-44d8-aa58-3aa16c9957fb	e1770a62-2997-4d34-9258-9300d62d5cbf	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	UNASSIGNED	Deepak Kumar (CG0005)	Assigned to Deepak Kumar. Priority: MEDIUM	2026-09-24 00:04:47.761408+05:30
78b0eb6d-6736-4448-98ba-96c8c4da1190	3ca55838-d953-4175-a37a-780ff438c869	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	ASSIGNMENT_CHANGE	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Deepak Kumar (CG0005)	Reassigned to Deepak Kumar. Reason: vjhg	2026-09-24 02:22:10.946805+05:30
7d7cab2c-d86b-40f0-aaec-006f24346ae4	3ca55838-d953-4175-a37a-780ff438c869	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	ASSIGNMENT_CHANGE	0438f197-65cc-4fb2-8667-bdaceee1db81	Super Admin (CG0001)	Reassigned to Super Admin. Reason: Reassigning to Admin for review	2026-09-24 02:23:24.979942+05:30
edf8a517-116e-4e6a-8dd7-949f91a05566	3ca55838-d953-4175-a37a-780ff438c869	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	ASSIGNMENT_CHANGE	de526836-5e73-49d7-9be3-8ad07caa6090	Mansi Singhal (CG0003)	Reassigned to Mansi Singhal. Reason: Assigning back to Mansi for operations workflow	2026-09-24 02:23:41.785719+05:30
c0982c75-4ccf-4e6e-99be-7bd7d2260bc3	3ca55838-d953-4175-a37a-780ff438c869	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	ASSIGNMENT_CHANGE	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Deepak Kumar (CG0005)	Reassigned to Deepak Kumar. Reason: yguyf	2026-09-24 02:25:05.275544+05:30
3269020c-f11a-4fd7-aebe-24ee42f7020e	4ea8e868-36ad-4bf1-8faa-6ab242e954bd	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	STATUS_CHANGE	NONE	UNASSIGNED	Order 'SO-2026-0003' confirmed and handed over from Sales.	2026-09-24 02:53:59.175861+05:30
c3c4c1ca-b8b9-4d60-8561-f5c2516ab80c	3997d4d2-bfb5-4a06-8cec-929270aeb419	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	STATUS_CHANGE	NONE	UNASSIGNED	Order 'SO-2026-0004' confirmed and handed over from Sales.	2026-09-24 02:54:54.6905+05:30
3b633802-1e91-44fb-9f6d-05fdc7f435a5	3997d4d2-bfb5-4a06-8cec-929270aeb419	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	UNASSIGNED	Mansi Singhal (CG0003)	Assigned to Mansi Singhal. Priority: MEDIUM	2026-09-24 03:23:14.086219+05:30
5704b42c-0775-4882-85a0-ede86f7ec192	e78b8f08-be2e-4424-9799-6895e872e8c2	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0005' confirmed and assigned by default to Operations Lead Mansi Singhal (CG0003).	2026-09-25 11:12:32.950864+05:30
f8099f91-d9a2-441a-8a43-518f049ed218	51d9ae10-f22d-448f-a560-c2a9323ffea8	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0006' confirmed and assigned to Mansi Singhal (CG0003).	2026-09-25 14:04:23.568611+05:30
5a9de352-af72-4174-a5d3-243f7be7a566	6bccf11d-68fe-4020-bac4-820936578bec	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0007' confirmed and assigned to Mansi Singhal (CG0003).	2026-09-25 14:06:06.490372+05:30
8d95b467-889d-4ca8-a820-006e0315a24f	6bccf11d-68fe-4020-bac4-820936578bec	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	ASSIGNMENT_CHANGE	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Deepak Kumar (CG0005)	Assigned to Deepak Kumar. Priority: MEDIUM	2026-09-25 14:06:46.200601+05:30
d07bd28d-bdae-4cbd-b3cd-32c151de714a	6bccf11d-68fe-4020-bac4-820936578bec	0438f197-65cc-4fb2-8667-bdaceee1db81	STATUS_CHANGE	ASSIGNED	IN_PROGRESS	Status changed from ASSIGNED to IN_PROGRESS	2026-09-25 23:15:13.887814+05:30
ad96d276-d526-497b-ae7e-cabf87d0a1a8	6bccf11d-68fe-4020-bac4-820936578bec	0438f197-65cc-4fb2-8667-bdaceee1db81	STATUS_CHANGE	IN_PROGRESS	PENDING_DOCUMENTS	Status changed from IN_PROGRESS to PENDING_DOCUMENTS	2026-09-25 23:15:19.833604+05:30
ec008316-3b89-4916-96a8-a15efefb7693	6bccf11d-68fe-4020-bac4-820936578bec	0438f197-65cc-4fb2-8667-bdaceee1db81	STATUS_CHANGE	PENDING_DOCUMENTS	IN_PROGRESS	Status changed from PENDING_DOCUMENTS to IN_PROGRESS	2026-09-25 23:15:21.164866+05:30
973ec049-4fe6-4703-ad42-fb16b10f60c1	6bccf11d-68fe-4020-bac4-820936578bec	0438f197-65cc-4fb2-8667-bdaceee1db81	STATUS_CHANGE	IN_PROGRESS	PENDING_DOCUMENTS	Status changed from IN_PROGRESS to PENDING_DOCUMENTS	2026-09-25 23:15:23.229833+05:30
63bf8e99-c14d-4178-9caf-8a9c2a1038a6	6bccf11d-68fe-4020-bac4-820936578bec	0438f197-65cc-4fb2-8667-bdaceee1db81	STATUS_CHANGE	PENDING_DOCUMENTS	IN_PROGRESS	Status changed from PENDING_DOCUMENTS to IN_PROGRESS	2026-09-25 23:15:24.079451+05:30
1388b8ec-9cf9-4e69-a047-f6aee2e4d1a7	6bccf11d-68fe-4020-bac4-820936578bec	0438f197-65cc-4fb2-8667-bdaceee1db81	STATUS_CHANGE	IN_PROGRESS	SUBMITTED	Status changed from IN_PROGRESS to SUBMITTED	2026-09-25 23:15:25.879441+05:30
fec2cc61-8683-4d8e-a787-b737a96d86b4	6bccf11d-68fe-4020-bac4-820936578bec	0438f197-65cc-4fb2-8667-bdaceee1db81	STATUS_CHANGE	SUBMITTED	APPROVED	Status changed from SUBMITTED to APPROVED	2026-09-25 23:15:28.014757+05:30
2aecf280-9709-43f2-ac25-91a8d45496bc	3ca55838-d953-4175-a37a-780ff438c869	0438f197-65cc-4fb2-8667-bdaceee1db81	STATUS_CHANGE	ASSIGNED	IN_PROGRESS	Status changed from ASSIGNED to IN_PROGRESS	2026-09-25 23:15:40.171223+05:30
a00ac82f-c28b-4fff-af61-a5e5540656e6	3ca55838-d953-4175-a37a-780ff438c869	0438f197-65cc-4fb2-8667-bdaceee1db81	STATUS_CHANGE	IN_PROGRESS	PENDING_DOCUMENTS	Status changed from IN_PROGRESS to PENDING_DOCUMENTS	2026-09-25 23:15:43.146614+05:30
010dc76f-fd91-46c9-a522-980408319836	3ca55838-d953-4175-a37a-780ff438c869	0438f197-65cc-4fb2-8667-bdaceee1db81	STATUS_CHANGE	PENDING_DOCUMENTS	IN_PROGRESS	Status changed from PENDING_DOCUMENTS to IN_PROGRESS	2026-09-25 23:15:45.753173+05:30
7c943df7-2af3-456d-9bcc-5f1e0c9dba9a	3ca55838-d953-4175-a37a-780ff438c869	0438f197-65cc-4fb2-8667-bdaceee1db81	STATUS_CHANGE	IN_PROGRESS	SUBMITTED	Status changed from IN_PROGRESS to SUBMITTED	2026-09-25 23:15:50.465858+05:30
de2e65ff-ca62-4a68-864d-07ff5411c3f0	3ca55838-d953-4175-a37a-780ff438c869	0438f197-65cc-4fb2-8667-bdaceee1db81	STATUS_CHANGE	SUBMITTED	APPROVED	Status changed from SUBMITTED to APPROVED	2026-09-25 23:15:54.664973+05:30
e98dd1c6-be40-41dd-ae22-338a1e5af45c	6bccf11d-68fe-4020-bac4-820936578bec	de526836-5e73-49d7-9be3-8ad07caa6090	SALES_UPDATE	Val:500000.00|Recvd:50000.00|Pmt:PARTIALLY_PAID	Val:500000|Recvd:500000|Pmt:FULLY_PAID	Sales order 'SO-2026-0007' updated: Advance Amount: ₹50,000 -> ₹5,00,000, Pending Amount: ₹4,50,000 -> ₹0, Payment Status: PARTIALLY_PAID -> FULLY_PAID	2026-09-26 00:10:25.694064+05:30
b7c13c09-031c-4198-b259-d86b9f6724e9	6bccf11d-68fe-4020-bac4-820936578bec	de526836-5e73-49d7-9be3-8ad07caa6090	SALES_UPDATE	Val:500000.00|Recvd:500000.00|Pmt:FULLY_PAID	Val:500000|Recvd:500000|Pmt:FULLY_PAID	Sales order 'SO-2026-0007' updated: No field changes detected.	2026-09-26 00:18:54.047101+05:30
c79be77c-9f8f-482d-8705-2e7d71354d23	e78b8f08-be2e-4424-9799-6895e872e8c2	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0005' deleted by Super Admin.	2026-09-26 01:20:21.453862+05:30
c89dc594-e6ea-4f49-b375-2e360e3dce4c	51d9ae10-f22d-448f-a560-c2a9323ffea8	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0006' deleted by Karishma Upadhyay.	2026-09-26 01:26:05.938047+05:30
1a26f3bf-26c8-45d6-910e-56d151a77c8e	6bccf11d-68fe-4020-bac4-820936578bec	0438f197-65cc-4fb2-8667-bdaceee1db81	REMARK_ADDED	\N	\N	Operations remark added: delay ho raha hai bhaii	2026-09-26 01:57:57.173187+05:30
e2079f23-0f07-4211-85f8-e70634856eae	6bccf11d-68fe-4020-bac4-820936578bec	0438f197-65cc-4fb2-8667-bdaceee1db81	REMARK_ADDED	\N	\N	Operations remark added: are bhaii bhaii	2026-09-26 02:14:02.775174+05:30
59ab92c1-da52-470d-8cb2-56e49224048b	db093cfd-6c3b-473c-ae66-9b295924aa36	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0008' confirmed and assigned to Mansi Singhal (CG0003).	2026-09-28 15:55:03.197591+05:30
9e975a9b-7206-481b-baf8-5c0084c97689	db093cfd-6c3b-473c-ae66-9b295924aa36	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Deepak Kumar (CG0005)	Assigned to Deepak Kumar. Priority: MEDIUM	2026-09-28 15:56:08.916015+05:30
6113fecc-f2fe-4d11-bdf0-d78971f03685	058b6bc8-9285-43fd-8c52-67532eb40ac6	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0009' confirmed and assigned to Mansi Singhal (CG0003).	2026-09-28 15:57:17.610013+05:30
c568ed54-115f-4a59-a064-d3bd4328658e	e0a66aa9-91bf-4214-85e2-5d8e270f2b23	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0010' confirmed and assigned to Mansi Singhal (CG0003).	2026-09-28 15:58:28.190352+05:30
72f02f09-a0e6-45f9-8186-d9be8a6efc6f	3ca55838-d953-4175-a37a-780ff438c869	0438f197-65cc-4fb2-8667-bdaceee1db81	REMARK_ADDED	\N	\N	Operations remark added: NOT POSSIBLE	2026-09-28 16:02:14.873895+05:30
109fbdac-89bd-4f6a-8eb4-8b1dc4f9da22	4ea8e868-36ad-4bf1-8faa-6ab242e954bd	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	UNASSIGNED	Mansi Singhal (CG0003)	Assigned to Mansi Singhal. Priority: MEDIUM	2026-09-29 00:37:37.287516+05:30
ed8840c5-4e7e-42bb-88ba-b6da7f88ffc9	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0011' confirmed and assigned to Mansi Singhal (CG0003).	2026-09-29 16:53:39.808136+05:30
ec24d48e-8453-4a97-a6de-6e918f142d53	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Deepak Kumar (CG0005)	Assigned to Deepak Kumar. Priority: MEDIUM	2026-09-29 16:54:24.198527+05:30
230448ec-2123-4743-a875-080f03c43ec4	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	STATUS_CHANGE	ASSIGNED	IN_PROGRESS	Status changed from ASSIGNED to IN_PROGRESS	2026-09-29 16:56:26.817097+05:30
a1699b25-34af-41ba-a2bd-d68b25264288	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	STATUS_CHANGE	IN_PROGRESS	SUBMITTED	Status changed from IN_PROGRESS to SUBMITTED	2026-09-29 16:56:29.620538+05:30
46f233a4-1a2b-4024-82d5-ba2f008ae03f	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	STATUS_CHANGE	SUBMITTED	APPROVED	Status changed from SUBMITTED to APPROVED	2026-09-29 16:56:36.303703+05:30
953404d2-fc96-423c-b52c-a8f64bcc77c2	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	REMARK_ADDED	\N	\N	Operations remark added: DHFGBLH	2026-09-29 16:57:03.827507+05:30
b32681cf-13e7-471c-827e-451168a024af	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	REMARK_ADDED	\N	\N	Operations remark added: GFDGFD,UF	2026-09-29 17:00:45.74438+05:30
729f073c-8a56-493f-b815-26f4ef2ca996	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	STATUS_CHANGE	SUBMITTED	AUTHORITY_QUERY	Status changed from SUBMITTED to AUTHORITY_QUERY	2026-09-29 16:56:31.816953+05:30
c1babe88-bc45-4e17-94ac-c08fc97bd4f3	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	STATUS_CHANGE	AUTHORITY_QUERY	IN_PROGRESS	Status changed from AUTHORITY_QUERY to IN_PROGRESS	2026-09-29 16:56:33.321767+05:30
2114943c-7268-44d5-8fc5-34b87ebbc086	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	STATUS_CHANGE	IN_PROGRESS	SUBMITTED	Status changed from IN_PROGRESS to SUBMITTED	2026-09-29 16:56:35.404833+05:30
dec8d253-7887-41d1-a83e-a1b6661e371f	543de9f0-dcb8-47b4-b98f-5b194e1258f3	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0012' confirmed and assigned to Mansi Singhal (CG0003).	2026-09-30 10:46:29.540439+05:30
414ee636-c116-46c4-baef-0dbd20e3e8b8	543de9f0-dcb8-47b4-b98f-5b194e1258f3	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Deepak Kumar (CG0005)	Reassigned to Deepak Kumar. Reason: lj2hfou34h2[4	2026-09-30 10:47:10.179705+05:30
6dca8e05-6f93-40e1-b892-acee60178b06	543de9f0-dcb8-47b4-b98f-5b194e1258f3	0438f197-65cc-4fb2-8667-bdaceee1db81	REMARK_ADDED	\N	\N	Operations remark added: jckthdctluvj	2026-09-30 10:49:18.104984+05:30
6f9dfb17-45dc-4fc9-a3cf-f62a12f2eb0b	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0013' confirmed and assigned to Mansi Singhal (CG0003).	2026-09-30 11:16:20.182113+05:30
0e0a6a99-8d03-403e-bdfa-afac0a307e1f	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	de526836-5e73-49d7-9be3-8ad07caa6090	ACCOUNTS_UPDATE	{"proforma_invoice_no": null, "tax_invoice_no": null, "reimbursement_note": null, "notes": null}	{"proforma_invoice_no": "sfvklflvdmfvlkmd"}	Accounts fields updated by Super Admin	2026-10-07 00:25:40.599569+05:30
d0824c32-fab4-4374-bee1-b6a7d9fc4ae1	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	de526836-5e73-49d7-9be3-8ad07caa6090	ACCOUNTS_UPDATE	{"proforma_invoice_no": "sfvklflvdmfvlkmd", "tax_invoice_no": null, "reimbursement_note": null, "notes": null}	{"tax_invoice_no": "dfm ,fd. dnlkdfn"}	Accounts fields updated by Super Admin	2026-10-07 00:25:45.311157+05:30
9c4b959c-55d0-44b3-bf33-af0f6ea1ce86	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	de526836-5e73-49d7-9be3-8ad07caa6090	ACCOUNTS_UPDATE	{"proforma_invoice_no": "sfvklflvdmfvlkmd", "tax_invoice_no": "dfm ,fd. dnlkdfn", "reimbursement_note": null, "notes": null}	{"reimbursement_note": "df vnf mv"}	Accounts fields updated by Super Admin	2026-10-07 00:25:49.615996+05:30
4231c82c-fc80-4393-8890-79d82e6419eb	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	de526836-5e73-49d7-9be3-8ad07caa6090	ACCOUNTS_UPDATE	{"proforma_invoice_no": "sfvklflvdmfvlkmd", "tax_invoice_no": "dfm ,fd. dnlkdfn", "reimbursement_note": "df vnf mv", "notes": null}	{"notes": "vdfb kjgfd"}	Accounts fields updated by Super Admin	2026-10-07 00:25:55.000682+05:30
767aea5b-a893-4569-9cf5-f3fa445b1bb2	0eef383e-ac4b-4541-a9a7-e0b98de5d548	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0014' confirmed and assigned to Mansi Singhal (CG0003).	2026-10-07 01:33:04.422815+05:30
06bc3b21-a75d-4a5f-bd62-b1dd7e5348ca	dece3eea-3f5b-46f5-9d7c-29ad9334097c	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0015' confirmed and assigned to Mansi Singhal (CG0003).	2026-10-07 01:33:59.33512+05:30
920d9f12-4964-407b-ae0b-1454d250d937	dece3eea-3f5b-46f5-9d7c-29ad9334097c	de526836-5e73-49d7-9be3-8ad07caa6090	ACCOUNTS_UPDATE	{"proforma_invoice_no": null, "tax_invoice_no": null, "reimbursement_note": null, "notes": null}	{"notes": "hello hunny bunny"}	Accounts fields updated by Super Admin	2026-10-07 01:34:16.352466+05:30
2a55625a-d84c-4629-b345-33faeef363cc	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0016' confirmed and assigned to Mansi Singhal (CG0003).	2026-10-07 16:08:17.554545+05:30
bec82e3e-7c92-451d-b54b-8af56e2f2001	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	ACCOUNTS_UPDATE	{"proforma_invoice_no": null, "tax_invoice_no": null, "reimbursement_note": null, "notes": null}	{"proforma_invoice_no": "ybyugf6gt"}	Accounts fields updated by Super Admin	2026-10-07 16:09:59.535562+05:30
fa0aa480-4658-4968-afc3-8512a459996d	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	ACCOUNTS_UPDATE	{"proforma_invoice_no": "ybyugf6gt", "tax_invoice_no": null, "reimbursement_note": null, "notes": null}	{"tax_invoice_no": "vtcfr5"}	Accounts fields updated by Super Admin	2026-10-07 16:10:04.821505+05:30
19ea29fc-0f51-4a04-ac04-b04d0a3e34ba	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	ACCOUNTS_UPDATE	{"proforma_invoice_no": "ybyugf6gt", "tax_invoice_no": "vtcfr5", "reimbursement_note": null, "notes": null}	{"reimbursement_note": "vftcvt"}	Accounts fields updated by Super Admin	2026-10-07 16:10:10.704298+05:30
8c923294-8841-458f-b9d2-93cd6ad296cb	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Deepak Kumar (CG0005)	Reassigned to Deepak Kumar. Reason: asdfgh	2026-10-07 16:20:18.561035+05:30
9faad7a1-45ab-44ca-8175-30c30111780e	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	REMARK_ADDED	\N	\N	Remark added by Super Admin (Administration): hello start the conversation	2026-10-08 23:54:50.534083+05:30
7b517e96-04a7-4434-8869-488e7f36b650	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	REMARK_ADDED	\N	\N	Remark added by Super Admin (Administration): hello secound conversation	2026-10-08 23:55:18.48581+05:30
e7f135e2-a771-4db6-880c-5981c6b6d74e	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	REMARK_ADDED	\N	\N	Remark added by Super Admin (Administration): last conversation	2026-10-08 23:55:43.270509+05:30
025fd824-6e62-4b6d-ad47-da329e8eef9b	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	0438f197-65cc-4fb2-8667-bdaceee1db81	REMARK_ADDED	\N	\N	Remark added by Deepak Kumar (Operations): hello testing	2026-10-09 00:01:05.271678+05:30
d0f97c81-521d-47b0-b3c9-87a1e14c0729	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	0438f197-65cc-4fb2-8667-bdaceee1db81	REMARK_ADDED	\N	\N	Remark added by Deepak Kumar (Operations): kya bhaii sucessfull ho gya kya	2026-10-09 00:36:13.554952+05:30
c3b2ff39-3143-48fc-8a4d-bf64eb7921d8	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	REMARK_ADDED	\N	\N	Remark added by Super Admin (Administration): haa siir	2026-10-09 00:36:26.799785+05:30
c650f01c-23b3-430e-bb39-55f26eaee271	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	REMARK_ADDED	\N	\N	Remark added by Karishma Upadhyay (Sales): hello gyus	2026-10-09 00:37:41.385078+05:30
4bc37b06-1901-4532-b3c9-4e6ba51dc62e	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	REMARK_ADDED	\N	\N	Remark added by Karishma Upadhyay (Sales): kya bhaii moj kr di lala heheh	2026-10-09 01:04:16.537733+05:30
e5f920ec-fc13-4ca6-ae0c-733a10245ae4	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	REMARK_ADDED	\N	\N	Remark added by Super Admin (Administration): or bhaiiiii aa gya swaad	2026-10-09 13:39:28.465619+05:30
ad52608e-2426-474c-8d98-928bde212c6e	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	REMARK_ADDED	\N	\N	Remark added by Super Admin (Administration): heheh haaji	2026-10-09 13:54:56.270212+05:30
d6170a9d-5895-4af7-9dc4-1b83b898c0c9	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	REMARK_ADDED	\N	\N	Remark added by Karishma Upadhyay (Sales): ky hai	2026-10-09 13:55:11.209514+05:30
07f720c7-3054-4901-bc13-666193431c52	0eef383e-ac4b-4541-a9a7-e0b98de5d548	de526836-5e73-49d7-9be3-8ad07caa6090	REMARK_ADDED	\N	\N	Remark added by Super Admin (Administration): next to next	2026-10-09 13:55:32.769987+05:30
1509c85c-64db-4a1e-b704-06e34e309522	dece3eea-3f5b-46f5-9d7c-29ad9334097c	de526836-5e73-49d7-9be3-8ad07caa6090	SALES_UPDATE	Val:1000000.00|Recvd:1.00|Pmt:PARTIALLY_PAID	Val:1000000|Recvd:1|Pmt:PARTIALLY_PAID	Sales order 'SO-2026-0015' updated: Remarks: hello hunny bunny -> hello guyss	2026-10-09 15:42:31.759614+05:30
a34ad71a-ef74-4243-b727-6af10e4a45a3	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0017' confirmed and assigned to Mansi Singhal (CG0003).	2026-10-09 19:03:35.633475+05:30
7bbd1e71-504d-4896-b065-ce4d2b53e414	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Deepak Kumar (CG0005)	Reassigned to Deepak Kumar. Reason: hv cftc	2026-10-09 19:19:17.922373+05:30
757b221d-e472-4663-8c7e-a13e22381252	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	REMARK_ADDED	\N	\N	Remark added by Super Admin (Administration): hb ygv	2026-10-09 19:19:26.029788+05:30
db7f0e17-cce8-4547-934d-871761814e99	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	0438f197-65cc-4fb2-8667-bdaceee1db81	Abhishek Kumar (CG0007)	Reassigned to Abhishek Kumar. Reason: vfty6cfty	2026-10-09 19:21:57.479945+05:30
1339d177-d4f6-4ef3-ac78-56411035a6ef	da56b220-e470-4487-a407-48645b60dbdc	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (CG0003)	Order 'SO-2026-0018' confirmed and assigned to Mansi Singhal (CG0003).	2026-10-09 19:27:56.209419+05:30
6ffc2af1-dd89-43f1-99f6-6b77f5beee04	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	REMARK_ADDED	\N	\N	Remark added by Super Admin (Administration): CALL AKASH 456789	2026-10-09 19:34:33.962955+05:30
599a637b-5941-4f96-8016-fd8cb5a7d270	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	ACCOUNTS_UPDATE	{"proforma_invoice_no": null, "tax_invoice_no": null, "reimbursement_note": null, "notes": "CALL AKASH 456789"}	{"proforma_invoice_no": "24562772"}	Accounts fields updated by Super Admin	2026-10-09 19:52:24.810186+05:30
498a781a-c456-4657-bf79-8d4dc3cfe341	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	ACCOUNTS_UPDATE	{"proforma_invoice_no": "24562772", "tax_invoice_no": null, "reimbursement_note": null, "notes": "CALL AKASH 456789"}	{"tax_invoice_no": "63782882"}	Accounts fields updated by Super Admin	2026-10-09 19:54:38.611067+05:30
cd0669a7-6f96-42d9-8814-303d9849dbb2	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	ACCOUNTS_UPDATE	{"proforma_invoice_no": "24562772", "tax_invoice_no": "63782882", "reimbursement_note": null, "notes": "CALL AKASH 456789"}	{"reimbursement_note": "2672377823"}	Accounts fields updated by Super Admin	2026-10-09 19:54:42.815985+05:30
6e99008f-fdd8-44e7-995a-fea66067bb51	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	8554d145-bdd4-4ee6-b821-74b73cfe40bf	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0019' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-10 02:44:56.415556+05:30
c569b32e-53c3-476b-9388-177944c806af	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	ASSIGNMENT_CHANGE	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Hrithik Choudhary (GC0008)	Reassigned to Hrithik Choudhary. Reason: hrithik ye task aab tm dekhoge	2026-10-10 02:51:37.01459+05:30
360667a4-aab1-462c-a446-d8a4e9659f08	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	65b43201-4875-4caa-a601-b0b535019b48	REMARK_ADDED	\N	\N	Operations remark added: site naii chal rahahia	2026-10-10 02:52:52.429684+05:30
7f13d7ac-a42d-4d77-9744-ecdd1e30087a	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	65b43201-4875-4caa-a601-b0b535019b48	STATUS_CHANGE	ASSIGNED	IN_PROGRESS	Status changed from ASSIGNED to IN_PROGRESS	2026-10-10 02:53:04.333608+05:30
c0ecddf7-44af-4eed-b6c8-df137e99913a	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	65b43201-4875-4caa-a601-b0b535019b48	STATUS_CHANGE	IN_PROGRESS	READY_FOR_SUBMISSION	Status changed from IN_PROGRESS to READY_FOR_SUBMISSION	2026-10-10 02:53:17.242599+05:30
60786595-77cc-48e9-80e1-69d5fa359e42	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	65b43201-4875-4caa-a601-b0b535019b48	STATUS_CHANGE	READY_FOR_SUBMISSION	SUBMITTED	Status changed from READY_FOR_SUBMISSION to SUBMITTED	2026-10-10 02:53:20.323383+05:30
296a2eaa-979d-468d-bc94-4f2898341e7c	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	65b43201-4875-4caa-a601-b0b535019b48	STATUS_CHANGE	SUBMITTED	APPROVED	Status changed from SUBMITTED to APPROVED	2026-10-10 02:53:22.853771+05:30
3a2e91a7-53b2-4c9d-b6dc-82784484da64	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	65b43201-4875-4caa-a601-b0b535019b48	REMARK_ADDED	\N	\N	Operations remark added: done mera kaam ho gy ahai	2026-10-10 02:53:42.079597+05:30
8133fa62-5b82-47ac-aff5-6b81ce186bba	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	0438f197-65cc-4fb2-8667-bdaceee1db81	REMARK_ADDED	\N	\N	Remark added by Deepak Kumar (Operations): haa ji paaji	2026-10-10 14:29:45.170322+05:30
6ffaa6d1-4a31-4b1e-99be-cf3a7619656a	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	65b43201-4875-4caa-a601-b0b535019b48	Deepak Kumar (GC0005)	Reassigned to Deepak Kumar. Reason: fhdrh	2026-10-10 18:23:56.579824+05:30
aa6a9ec6-0478-4208-b488-672b6ab68bb0	e1770a62-2997-4d34-9258-9300d62d5cbf	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:0438f197-65cc-4fb2-8667-bdaceee1db81	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0001' deleted by Super Admin.	2026-10-19 12:31:24.25362+05:30
24b38423-bd34-4945-816a-5e9993431bb6	4adf326f-6dda-4684-ab74-874667a59a0b	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0020' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-24 22:55:03.17085+05:30
9d53e921-be95-413f-aff1-6fb2df61dc9a	a939e2c4-35b9-47c9-9f8a-bc448c5bb877	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0021' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-24 22:56:52.733047+05:30
0506c717-18dd-442a-b1c7-1ae167487761	e32bf79c-e6e2-4615-b1f2-8040247c3f18	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0022' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-24 22:59:12.837226+05:30
1893f335-5911-4368-8319-975cdfdfb499	8553d61d-cce7-4877-8474-9a990c4ee4ec	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0023' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-25 22:19:21.553027+05:30
59e4cbc7-ff6f-454b-9d70-d4fc82091150	950cc940-dbb1-45e3-a4fc-276eced83899	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0024' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-25 22:19:21.553027+05:30
2efe8d4f-68e0-493c-85e5-190ead306d4c	bf7aa794-c1d2-452e-b6d3-ba838dd10b02	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0025' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-25 22:19:21.553027+05:30
642512ac-2455-463c-ad5c-d3b9c09c085f	2f3b7575-2066-493a-a62c-fc95be74d0fb	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0026' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-25 22:19:21.553027+05:30
3b7b32e2-a6b0-4d1f-9677-c3b02ed508f8	eaeea2ed-76f7-4b5a-a5be-a9f304b72275	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0027' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-25 22:19:21.553027+05:30
ac8bcba8-0148-4453-b755-e6259dcd6ae5	bf7aa794-c1d2-452e-b6d3-ba838dd10b02	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0025' deleted by Super Admin.	2026-10-25 23:01:44.739141+05:30
6eb97187-3720-44e4-9cd1-2a407f488a21	eaeea2ed-76f7-4b5a-a5be-a9f304b72275	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0027' deleted by Super Admin.	2026-10-25 23:01:48.002443+05:30
61ba761c-4219-4fe2-a09f-697b06da8601	2f3b7575-2066-493a-a62c-fc95be74d0fb	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0026' deleted by Super Admin.	2026-10-25 23:01:58.070864+05:30
e0c110c1-4214-43ba-8390-e4d7c55887cf	950cc940-dbb1-45e3-a4fc-276eced83899	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0024' deleted by Super Admin.	2026-10-25 23:02:05.343881+05:30
888ccea6-2b26-4f80-bc56-e229d12d2c92	8553d61d-cce7-4877-8474-9a990c4ee4ec	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0023' deleted by Super Admin.	2026-10-25 23:02:09.213476+05:30
ddcf41a9-ecb8-4f5e-8943-1b402d91a6a0	680e84cc-4054-49d2-b147-d6a86b5b9a13	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0028' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-25 23:04:54.377324+05:30
f20e2a6a-faaa-4828-87ab-c0a8cf2c3613	ca0c550f-6f0e-4b06-8466-66fc8b221831	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0029' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-25 23:37:35.72326+05:30
bb4858cb-74db-48ce-8344-d9e075ea5fcf	733b35e2-4330-4588-aa1f-5ec8d6df279c	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0030' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-25 23:37:35.72326+05:30
ec6c933b-cb9a-4478-bf95-a03c24c11bbf	71ae120b-7250-43d3-a092-ca60b8366bfa	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0031' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-25 23:37:35.72326+05:30
b383e8ec-9fe4-429d-a5ad-90a1a2c4bf31	5975e799-fb23-4f30-8f31-4338ed37ee4a	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0032' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-25 23:37:35.72326+05:30
886e2494-f77a-4853-82db-100ad555f995	2bed4f2b-61f3-45b0-bf20-474a212be9e3	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0033' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-25 23:37:35.72326+05:30
c03694bb-6ce5-4847-b2fa-4753c4ac22d3	2df25880-1b91-4ed4-9eb4-9aa54cb56f53	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0034' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-25 23:48:24.453326+05:30
00693a33-5594-4da1-b487-975f9ce9d02d	2df25880-1b91-4ed4-9eb4-9aa54cb56f53	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0034' deleted by Super Admin.	2026-10-25 23:52:16.203462+05:30
b4055a80-fb02-467d-bf4c-ccb53dbaf2d9	2bed4f2b-61f3-45b0-bf20-474a212be9e3	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0033' deleted by Super Admin.	2026-10-25 23:52:19.692351+05:30
909a044c-24e5-45e0-9dff-888d8e45cb81	71ae120b-7250-43d3-a092-ca60b8366bfa	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0031' deleted by Super Admin.	2026-10-25 23:52:22.243153+05:30
c0e683ad-e825-4256-9239-59cc5656dc25	ca0c550f-6f0e-4b06-8466-66fc8b221831	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0029' deleted by Super Admin.	2026-10-25 23:52:24.971144+05:30
28b4db67-c261-4d4b-ab4c-9cac8cd548f1	733b35e2-4330-4588-aa1f-5ec8d6df279c	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0030' deleted by Super Admin.	2026-10-25 23:52:27.691696+05:30
77f7a38d-2531-47c3-bc11-895f429b14fe	5975e799-fb23-4f30-8f31-4338ed37ee4a	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0032' deleted by Super Admin.	2026-10-25 23:52:29.732426+05:30
8c1cff77-0123-41fa-99f6-49f7cd852553	680e84cc-4054-49d2-b147-d6a86b5b9a13	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0028' deleted by Super Admin.	2026-10-25 23:52:37.604036+05:30
4e9f539f-6e67-476a-984f-ada303e2feee	f25069b3-5013-4ebb-82ef-cea01267657c	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0035' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-26 00:08:10.110917+05:30
68a1625f-2ec3-41ed-b9b8-69bfe97dd2dc	68bae788-12d3-40a8-97be-06ec36f8772e	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0036' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-26 00:08:10.110917+05:30
0b7e6635-93d9-4fcf-974b-e0561d757736	e5837191-599a-4c9d-ac0d-58f9e442045c	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0037' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-26 00:08:10.110917+05:30
a8f21584-caba-4811-86cc-8b6c643276fc	f05bb899-190f-40b0-b993-038e3011bf0b	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0038' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-26 00:08:10.110917+05:30
19492027-6321-4107-85f8-36b8ec2af6d3	38ce8f41-9a04-40d2-acc8-543390e99cbf	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0039' confirmed and assigned to Mansi Singhal (GC0003).	2026-10-26 00:08:10.110917+05:30
8b9700a7-390e-4f4d-9cd4-c6caeb56ef54	e5837191-599a-4c9d-ac0d-58f9e442045c	de526836-5e73-49d7-9be3-8ad07caa6090	STATUS_CHANGE	ASSIGNED	IN_PROGRESS	Status changed from ASSIGNED to IN_PROGRESS	2026-10-26 00:37:28.043619+05:30
9748c7f3-e54a-4186-a8da-7cb0bd94ab65	e5837191-599a-4c9d-ac0d-58f9e442045c	de526836-5e73-49d7-9be3-8ad07caa6090	STATUS_CHANGE	IN_PROGRESS	SUBMITTED	Status changed from IN_PROGRESS to SUBMITTED	2026-10-26 00:37:29.337175+05:30
a6fa1e52-003d-4f09-b6e3-078fcfc942f0	e5837191-599a-4c9d-ac0d-58f9e442045c	de526836-5e73-49d7-9be3-8ad07caa6090	STATUS_CHANGE	SUBMITTED	APPROVED	Status changed from SUBMITTED to APPROVED	2026-10-26 00:37:30.804914+05:30
fab12a53-cdcf-409d-8046-69c8a8f32212	e5837191-599a-4c9d-ac0d-58f9e442045c	de526836-5e73-49d7-9be3-8ad07caa6090	TASK_SOFT_DELETED	Status:APPROVED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	SoftDeleted|Status:APPROVED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Linked sales order 'SO-2026-0037' soft-deleted by Super Admin (Super Admin). Reason: giugiu	2026-10-26 00:38:04.067502+05:30
5f2be89f-1e06-4c2b-9923-5ea806bea6be	3ca55838-d953-4175-a37a-780ff438c869	de526836-5e73-49d7-9be3-8ad07caa6090	TASK_SOFT_DELETED	Status:APPROVED|Assignee:0438f197-65cc-4fb2-8667-bdaceee1db81	SoftDeleted|Status:APPROVED|Assignee:0438f197-65cc-4fb2-8667-bdaceee1db81	Linked sales order 'SO-2026-0002' soft-deleted by Super Admin (Super Admin). Reason: dummy entry	2026-10-31 12:06:12.829026+05:30
50ed9359-523c-40a4-896f-ed7eb3f86324	4ea8e868-36ad-4bf1-8faa-6ab242e954bd	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0003' deleted by Super Admin.	2026-10-31 12:06:20.914963+05:30
89b1a0e9-5467-4876-8fcc-07ff84ca97b7	3997d4d2-bfb5-4a06-8cec-929270aeb419	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0004' deleted by Super Admin.	2026-10-31 12:06:31.54437+05:30
9556fb1c-09d0-4481-a496-f6fcfd5cb81e	db093cfd-6c3b-473c-ae66-9b295924aa36	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:0438f197-65cc-4fb2-8667-bdaceee1db81	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0008' deleted by Super Admin.	2026-10-31 12:07:01.349678+05:30
77ad41ef-bc05-478a-9bb7-fc000bbcaa57	6bccf11d-68fe-4020-bac4-820936578bec	de526836-5e73-49d7-9be3-8ad07caa6090	TASK_SOFT_DELETED	Status:APPROVED|Assignee:0438f197-65cc-4fb2-8667-bdaceee1db81	SoftDeleted|Status:APPROVED|Assignee:0438f197-65cc-4fb2-8667-bdaceee1db81	Linked sales order 'SO-2026-0007' soft-deleted by Super Admin (Super Admin). Reason: dummy entry	2026-10-31 12:07:16.834664+05:30
cc020ab9-d395-4b3d-bd03-b8b6e430acf9	058b6bc8-9285-43fd-8c52-67532eb40ac6	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0009' deleted by Super Admin.	2026-10-31 12:07:21.439531+05:30
ac9c5c30-2caa-4e16-ba2a-5e0d59caaf97	e0a66aa9-91bf-4214-85e2-5d8e270f2b23	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0010' deleted by Super Admin.	2026-10-31 12:07:26.169987+05:30
bbdb50ff-6a9c-4b17-aacb-bb64c1f1cf87	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	TASK_SOFT_DELETED	Status:APPROVED|Assignee:0438f197-65cc-4fb2-8667-bdaceee1db81	SoftDeleted|Status:APPROVED|Assignee:0438f197-65cc-4fb2-8667-bdaceee1db81	Linked sales order 'SO-2026-0011' soft-deleted by Super Admin (Super Admin). Reason: dummy entry	2026-10-31 12:07:34.927719+05:30
8c59e6a1-2e2a-47e9-938a-27ab4c07fe6c	543de9f0-dcb8-47b4-b98f-5b194e1258f3	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:0438f197-65cc-4fb2-8667-bdaceee1db81	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0012' deleted by Super Admin.	2026-10-31 12:07:38.988466+05:30
c2fa6b06-fde4-45a9-af2b-1f64f4e35165	f25069b3-5013-4ebb-82ef-cea01267657c	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0035' deleted by Super Admin.	2026-10-31 12:07:42.118273+05:30
3b7f17a8-f3aa-44fb-9d09-32c8be1d6778	38ce8f41-9a04-40d2-acc8-543390e99cbf	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0039' deleted by Super Admin.	2026-10-31 12:07:44.815731+05:30
4d545f7e-0a0b-4c96-992e-dc4f148c9f6a	f05bb899-190f-40b0-b993-038e3011bf0b	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0038' deleted by Super Admin.	2026-10-31 12:07:47.483113+05:30
b93f19bf-49d4-4e16-a049-8b97a4040664	68bae788-12d3-40a8-97be-06ec36f8772e	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0036' deleted by Super Admin.	2026-10-31 12:07:50.067049+05:30
42589fce-85b0-4995-bb79-8c1dd23ae04a	e32bf79c-e6e2-4615-b1f2-8040247c3f18	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0022' deleted by Super Admin.	2026-10-31 12:07:52.658268+05:30
48b97520-aaae-42ba-aa8a-e8b9853d37a4	a939e2c4-35b9-47c9-9f8a-bc448c5bb877	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0021' deleted by Super Admin.	2026-10-31 12:07:56.549579+05:30
2bee3e70-85b2-4646-ae3e-70eaf348c57b	4adf326f-6dda-4684-ab74-874667a59a0b	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0020' deleted by Super Admin.	2026-10-31 12:07:59.544928+05:30
9a946bf7-d569-45f4-9c50-a6b80dbabecf	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	de526836-5e73-49d7-9be3-8ad07caa6090	TASK_SOFT_DELETED	Status:APPROVED|Assignee:0438f197-65cc-4fb2-8667-bdaceee1db81	SoftDeleted|Status:APPROVED|Assignee:0438f197-65cc-4fb2-8667-bdaceee1db81	Linked sales order 'SO-2026-0019' soft-deleted by Super Admin (Super Admin). Reason: Dummy entry	2026-10-31 12:08:09.740188+05:30
5593ae4a-df96-44a5-8e43-7c6a5c7550ef	da56b220-e470-4487-a407-48645b60dbdc	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0018' deleted by Super Admin.	2026-10-31 12:08:13.643257+05:30
3d5bbc32-56ae-4652-a6d3-530cfda47bb9	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:dcdee779-494b-4fe7-afa1-d3b66c784fbb	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0017' deleted by Super Admin.	2026-10-31 12:08:16.495194+05:30
b9924d3e-1f1f-49fc-9755-628936fb75b4	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:0438f197-65cc-4fb2-8667-bdaceee1db81	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0016' deleted by Super Admin.	2026-10-31 12:08:18.874935+05:30
0816012c-3927-48c0-bf55-541628d1d127	dece3eea-3f5b-46f5-9d7c-29ad9334097c	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0015' deleted by Super Admin.	2026-10-31 12:08:21.379945+05:30
db20dbdf-02b4-40c3-9821-f24fa5e38a02	0eef383e-ac4b-4541-a9a7-e0b98de5d548	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0014' deleted by Super Admin.	2026-10-31 12:08:23.87694+05:30
f509458a-6fd2-4675-b59d-3b3cd6d18f36	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	de526836-5e73-49d7-9be3-8ad07caa6090	APPLICATION_CANCELLED	Status:ASSIGNED|Assignee:84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Status:CANCELLED|Assignee:None	Sales order 'SO-2026-0013' deleted by Super Admin.	2026-10-31 12:08:28.590881+05:30
42dbe900-9bb8-4e52-b630-3769f4684716	7b2791ff-c6bc-4ebe-9dbc-bec76ce3bdd5	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0040' confirmed and assigned to Mansi Singhal (GC0003).	2026-11-01 18:41:07.525029+05:30
182da559-b54b-48be-a250-27a096084178	4196c2a9-282c-40ee-8a75-2aebc5eef45d	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0041' confirmed and assigned to Mansi Singhal (GC0003).	2026-11-01 18:42:14.74885+05:30
95b6d51c-e052-4710-8003-3692e735098a	3f2029b1-d446-46d9-960e-5ee9e676dd71	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0042' confirmed and assigned to Mansi Singhal (GC0003).	2026-11-01 18:42:14.74885+05:30
82ff429e-7896-43a2-9354-510dff5c3cb5	7f96f52b-ecc5-4172-a5e6-7018ebb135d7	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0043' confirmed and assigned to Mansi Singhal (GC0003).	2026-11-01 18:42:14.74885+05:30
a0bb3553-8ac8-43b7-9a3f-9bdb90a0e66c	68d5f2f9-a3a6-469c-b790-6ff2f5da8529	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0044' confirmed and assigned to Mansi Singhal (GC0003).	2026-11-01 18:42:14.74885+05:30
11a914be-11dc-435e-a029-eee00f7ccb61	342cb97c-953e-4643-bd89-7a2bd88ec2e8	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	NONE	Mansi Singhal (GC0003)	Order 'SO-2026-0045' confirmed and assigned to Mansi Singhal (GC0003).	2026-11-01 18:42:14.74885+05:30
0134a29e-cda4-4117-a2bd-fc5425cd57b8	342cb97c-953e-4643-bd89-7a2bd88ec2e8	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Hrithik Choudhary (GC0008)	Reassigned to Hrithik Choudhary. Reason: xcvfds	2026-11-02 18:36:14.450267+05:30
12c6a69c-fa9c-42dc-909e-cd9e33552ed2	7b2791ff-c6bc-4ebe-9dbc-bec76ce3bdd5	de526836-5e73-49d7-9be3-8ad07caa6090	ASSIGNMENT_CHANGE	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Deepak Kumar (GC0005)	Reassigned to Deepak Kumar. Reason: asdfa	2026-11-02 18:36:38.2648+05:30
\.


--
-- Data for Name: application_assignment_history; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.application_assignment_history (history_id, application_id, assigned_by_user_id, previous_assignee_user_id, new_assignee_user_id, reason, assigned_at) FROM stdin;
935eacf8-9293-4551-8944-3c5a5d1d909a	3ca55838-d953-4175-a37a-780ff438c869	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	test entery\n	2026-09-24 00:04:08.467409+05:30
f9c3d6d5-3e93-422f-b425-cbecc6093132	e1770a62-2997-4d34-9258-9300d62d5cbf	de526836-5e73-49d7-9be3-8ad07caa6090	\N	0438f197-65cc-4fb2-8667-bdaceee1db81	twst2	2026-09-24 00:04:47.770945+05:30
a6aca168-8957-402d-95c1-9629645aa35d	3ca55838-d953-4175-a37a-780ff438c869	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0438f197-65cc-4fb2-8667-bdaceee1db81	vjhg	2026-09-24 02:22:10.946805+05:30
2ace11f3-1417-446b-b7bd-c43605f4777c	3ca55838-d953-4175-a37a-780ff438c869	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0438f197-65cc-4fb2-8667-bdaceee1db81	de526836-5e73-49d7-9be3-8ad07caa6090	Reassigning to Admin for review	2026-09-24 02:23:24.979942+05:30
ab1a4939-617a-442f-a13f-57b225a24a07	3ca55838-d953-4175-a37a-780ff438c869	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Assigning back to Mansi for operations workflow	2026-09-24 02:23:41.785719+05:30
ac9f9f99-8815-43db-93a8-db9a4763688b	3ca55838-d953-4175-a37a-780ff438c869	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0438f197-65cc-4fb2-8667-bdaceee1db81	yguyf	2026-09-24 02:25:05.275544+05:30
66a1e33a-7c4b-4cc0-b07b-b7a9377aead1	3997d4d2-bfb5-4a06-8cec-929270aeb419	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment	2026-09-24 03:23:14.086219+05:30
9cf04344-8fe8-4b87-bf7f-6d1c1f525322	e78b8f08-be2e-4424-9799-6895e872e8c2	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Automatic default assignment on sales entry confirmation	2026-09-25 11:12:33.009191+05:30
c97791e0-e263-4b5b-a692-b16b5ccb805d	51d9ae10-f22d-448f-a560-c2a9323ffea8	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-09-25 14:04:23.600944+05:30
a403923a-ac8d-468e-b21a-8afc36e8d218	6bccf11d-68fe-4020-bac4-820936578bec	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-09-25 14:06:06.511792+05:30
38b6f239-3d03-4b1e-bb60-03dbba6e8fbd	6bccf11d-68fe-4020-bac4-820936578bec	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0438f197-65cc-4fb2-8667-bdaceee1db81	Initial task assignment	2026-09-25 14:06:46.200601+05:30
50da7e14-8471-40c9-9b78-6a6f3df57106	e78b8f08-be2e-4424-9799-6895e872e8c2	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0005' deleted by Super Admin.	2026-09-26 01:20:21.453551+05:30
35c8a239-a88f-4dc6-a633-7bc58ca6a58d	51d9ae10-f22d-448f-a560-c2a9323ffea8	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0006' deleted by Karishma Upadhyay.	2026-09-26 01:26:05.937845+05:30
b6dcf691-9426-4cfe-955f-ecbc00a621bc	db093cfd-6c3b-473c-ae66-9b295924aa36	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-09-28 15:55:03.236226+05:30
9c42c5b9-d3a6-4098-96f2-dd3250b5f946	db093cfd-6c3b-473c-ae66-9b295924aa36	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0438f197-65cc-4fb2-8667-bdaceee1db81	urgent	2026-09-28 15:56:08.916015+05:30
11e4a3a2-7cbc-4a3a-96a1-affa2428884d	058b6bc8-9285-43fd-8c52-67532eb40ac6	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-09-28 15:57:17.640968+05:30
685206a4-4bd7-44d3-b106-d7917568ac36	e0a66aa9-91bf-4214-85e2-5d8e270f2b23	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-09-28 15:58:28.217222+05:30
a659ace4-9f34-49fb-bfc9-9399581eacf9	4ea8e868-36ad-4bf1-8faa-6ab242e954bd	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment	2026-09-29 00:37:37.287516+05:30
65313a00-9452-4aeb-984e-e19a95f643cb	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-09-29 16:53:39.847958+05:30
12e9cca3-b160-41c7-89d4-0bcc85007281	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0438f197-65cc-4fb2-8667-bdaceee1db81	Initial task assignment	2026-09-29 16:54:24.198527+05:30
332ac16f-c51a-4014-be18-5c16d0e65d2a	543de9f0-dcb8-47b4-b98f-5b194e1258f3	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-09-30 10:46:29.5856+05:30
1f215c33-6aca-4b3d-ad69-0bb03253d031	543de9f0-dcb8-47b4-b98f-5b194e1258f3	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0438f197-65cc-4fb2-8667-bdaceee1db81	lj2hfou34h2[4	2026-09-30 10:47:10.179705+05:30
94cd4f46-2353-43aa-a2e0-2772565893f0	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-09-30 11:16:20.224252+05:30
2d24bc65-aaaa-475b-b0b8-f4dd4c2af703	0eef383e-ac4b-4541-a9a7-e0b98de5d548	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-07 01:33:04.45794+05:30
4af1be3f-e482-495e-a227-976e99462428	dece3eea-3f5b-46f5-9d7c-29ad9334097c	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-07 01:33:59.349217+05:30
fa207f15-3454-43d3-9513-49ffc3014dc8	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-07 16:08:17.601928+05:30
0b593b54-b607-46e2-945e-d2d1dd2d7101	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0438f197-65cc-4fb2-8667-bdaceee1db81	asdfgh	2026-10-07 16:20:18.561035+05:30
a7251dcb-ad22-499b-8892-c4dc70ab3fd6	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-09 19:03:35.685795+05:30
ed226b3a-38da-47c7-897e-4a33a4c9db5b	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0438f197-65cc-4fb2-8667-bdaceee1db81	hv cftc	2026-10-09 19:19:17.922373+05:30
31140720-57c7-4342-b3ab-6b0c2549193b	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	0438f197-65cc-4fb2-8667-bdaceee1db81	dcdee779-494b-4fe7-afa1-d3b66c784fbb	vfty6cfty	2026-10-09 19:21:57.479945+05:30
c40060b4-fc2d-4b13-be2d-ee9a4c8eefb4	da56b220-e470-4487-a407-48645b60dbdc	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-09 19:27:56.248847+05:30
508860d3-2526-425f-9b98-323c93ddae84	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	8554d145-bdd4-4ee6-b821-74b73cfe40bf	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-10 02:44:56.482069+05:30
a169127c-169b-4dc8-a17f-7713fd90d9ec	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	65b43201-4875-4caa-a601-b0b535019b48	hrithik ye task aab tm dekhoge	2026-10-10 02:51:37.01459+05:30
54faeea8-06d3-45cf-9ac5-fa2391e349ad	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	de526836-5e73-49d7-9be3-8ad07caa6090	65b43201-4875-4caa-a601-b0b535019b48	0438f197-65cc-4fb2-8667-bdaceee1db81	fhdrh	2026-10-10 18:23:56.579824+05:30
e8bba9c8-6cef-449d-b21a-22a19cec9ee4	e1770a62-2997-4d34-9258-9300d62d5cbf	de526836-5e73-49d7-9be3-8ad07caa6090	0438f197-65cc-4fb2-8667-bdaceee1db81	\N	Sales entry 'SO-2026-0001' deleted by Super Admin.	2026-10-19 12:31:24.253481+05:30
8339fca9-ebfb-4c33-ab76-b591d110918f	4adf326f-6dda-4684-ab74-874667a59a0b	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-24 22:55:03.214409+05:30
083d4b7e-1442-4c62-a251-e20772d6d1f1	a939e2c4-35b9-47c9-9f8a-bc448c5bb877	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-24 22:56:52.756781+05:30
ba9071cf-323b-4608-9697-49adeff67954	e32bf79c-e6e2-4615-b1f2-8040247c3f18	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-24 22:59:12.869192+05:30
0dd8d51f-5c5c-402c-b9b7-6572a607d1ba	8553d61d-cce7-4877-8474-9a990c4ee4ec	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-25 22:19:21.606159+05:30
7580b89b-3cf7-44c8-96c7-1e4cec42c06c	950cc940-dbb1-45e3-a4fc-276eced83899	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-25 22:19:21.671225+05:30
c7eb70c6-8012-435c-8f32-e586e9c1f76c	bf7aa794-c1d2-452e-b6d3-ba838dd10b02	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-25 22:19:21.689015+05:30
0fb91240-2139-4c75-a735-c528ad4c2b29	2f3b7575-2066-493a-a62c-fc95be74d0fb	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-25 22:19:21.717474+05:30
8ad50e88-2fcf-49e6-bac7-3265c8a508f5	eaeea2ed-76f7-4b5a-a5be-a9f304b72275	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-25 22:19:21.750756+05:30
786849af-6674-497d-9ac3-b39f823c08cf	bf7aa794-c1d2-452e-b6d3-ba838dd10b02	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0025' deleted by Super Admin.	2026-10-25 23:01:44.739141+05:30
dcc65ccb-3fea-43bb-999d-e9369f8f4e8c	eaeea2ed-76f7-4b5a-a5be-a9f304b72275	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0027' deleted by Super Admin.	2026-10-25 23:01:48.002443+05:30
b4b678b5-403c-464c-bd99-ad99da2fd44c	2f3b7575-2066-493a-a62c-fc95be74d0fb	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0026' deleted by Super Admin.	2026-10-25 23:01:58.070864+05:30
b81a4e2a-8a55-4de9-8e98-6a3aec6d8007	950cc940-dbb1-45e3-a4fc-276eced83899	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0024' deleted by Super Admin.	2026-10-25 23:02:05.343881+05:30
a6daeaac-f6d5-4b19-95a9-be4681d7b296	8553d61d-cce7-4877-8474-9a990c4ee4ec	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0023' deleted by Super Admin.	2026-10-25 23:02:09.213476+05:30
4ddf7c3d-2ceb-4926-ae7f-ce3835805fc8	680e84cc-4054-49d2-b147-d6a86b5b9a13	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-25 23:04:54.405026+05:30
206ddf80-b04e-48b6-a9a7-ba675e61af7a	ca0c550f-6f0e-4b06-8466-66fc8b221831	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-25 23:37:35.760523+05:30
bb01f219-1551-4991-a6aa-746a7ae88497	733b35e2-4330-4588-aa1f-5ec8d6df279c	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-25 23:37:35.803022+05:30
d2dd7d06-045b-4c68-a1c3-e005c2735ae2	71ae120b-7250-43d3-a092-ca60b8366bfa	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-25 23:37:35.822343+05:30
5cb9630f-337f-4eda-813d-15dcf8e88975	5975e799-fb23-4f30-8f31-4338ed37ee4a	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-25 23:37:35.841892+05:30
ce14fbc1-30bb-41ec-a93d-00ee7ad7e7f3	2bed4f2b-61f3-45b0-bf20-474a212be9e3	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-25 23:37:35.86555+05:30
692cdedd-3c18-464e-a992-67710fe0adac	2df25880-1b91-4ed4-9eb4-9aa54cb56f53	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-25 23:48:24.484026+05:30
b7e7199f-15e9-4955-b65b-1f00698285d1	2df25880-1b91-4ed4-9eb4-9aa54cb56f53	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0034' deleted by Super Admin.	2026-10-25 23:52:16.203462+05:30
700459c7-7f11-46ee-9138-d1d50516ce98	2bed4f2b-61f3-45b0-bf20-474a212be9e3	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0033' deleted by Super Admin.	2026-10-25 23:52:19.692351+05:30
04bda1e9-c0af-4717-a757-cc00c2fbe4e3	71ae120b-7250-43d3-a092-ca60b8366bfa	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0031' deleted by Super Admin.	2026-10-25 23:52:22.243153+05:30
73323ae2-f7e7-43ad-90cd-15b75f747b17	ca0c550f-6f0e-4b06-8466-66fc8b221831	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0029' deleted by Super Admin.	2026-10-25 23:52:24.971144+05:30
3a496791-ea5d-4abf-afbe-f07a21f05353	733b35e2-4330-4588-aa1f-5ec8d6df279c	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0030' deleted by Super Admin.	2026-10-25 23:52:27.691696+05:30
dc69182c-1ed5-4d0f-a9b8-98380ed18dd9	5975e799-fb23-4f30-8f31-4338ed37ee4a	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0032' deleted by Super Admin.	2026-10-25 23:52:29.732426+05:30
bd5fb535-e5b9-496e-b1b4-e23c7994c012	680e84cc-4054-49d2-b147-d6a86b5b9a13	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0028' deleted by Super Admin.	2026-10-25 23:52:37.604036+05:30
760a7354-c550-4e64-8096-daa2077801d8	f25069b3-5013-4ebb-82ef-cea01267657c	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-26 00:08:10.155718+05:30
92a20bfa-2688-407d-a75a-92da3822fe1c	68bae788-12d3-40a8-97be-06ec36f8772e	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-26 00:08:10.204686+05:30
b8d6eb84-a608-4c62-905f-d9d29b43ccda	e5837191-599a-4c9d-ac0d-58f9e442045c	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-26 00:08:10.226672+05:30
32e86477-257a-4204-840d-fc603fb634b9	f05bb899-190f-40b0-b993-038e3011bf0b	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-26 00:08:10.249106+05:30
7ce09762-a9ad-4af3-9091-610d9cec1baa	38ce8f41-9a04-40d2-acc8-543390e99cbf	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-10-26 00:08:10.276566+05:30
14873759-ed4b-4d74-a3fb-fddd5a4e03d5	4ea8e868-36ad-4bf1-8faa-6ab242e954bd	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0003' deleted by Super Admin.	2026-10-31 12:06:20.914963+05:30
326be0af-1d0c-42f4-9367-d611b66ede74	3997d4d2-bfb5-4a06-8cec-929270aeb419	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0004' deleted by Super Admin.	2026-10-31 12:06:31.54437+05:30
325d94a9-3193-40f9-a388-1fec3581d272	db093cfd-6c3b-473c-ae66-9b295924aa36	de526836-5e73-49d7-9be3-8ad07caa6090	0438f197-65cc-4fb2-8667-bdaceee1db81	\N	Sales entry 'SO-2026-0008' deleted by Super Admin.	2026-10-31 12:07:01.349678+05:30
7844e0c6-03fc-40a3-9eed-ee4d64ee5155	058b6bc8-9285-43fd-8c52-67532eb40ac6	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0009' deleted by Super Admin.	2026-10-31 12:07:21.439531+05:30
26679883-00d4-499d-8924-0a222e110418	e0a66aa9-91bf-4214-85e2-5d8e270f2b23	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0010' deleted by Super Admin.	2026-10-31 12:07:26.169987+05:30
071b2c30-70f1-41c9-9f6c-29be03abca13	543de9f0-dcb8-47b4-b98f-5b194e1258f3	de526836-5e73-49d7-9be3-8ad07caa6090	0438f197-65cc-4fb2-8667-bdaceee1db81	\N	Sales entry 'SO-2026-0012' deleted by Super Admin.	2026-10-31 12:07:38.988466+05:30
8806598c-c334-41ad-b87d-c672b7315f2c	f25069b3-5013-4ebb-82ef-cea01267657c	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0035' deleted by Super Admin.	2026-10-31 12:07:42.118273+05:30
c8d435a2-d468-4dc5-b269-52cbf365e327	38ce8f41-9a04-40d2-acc8-543390e99cbf	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0039' deleted by Super Admin.	2026-10-31 12:07:44.815731+05:30
0b0c477a-83ce-4684-a11e-1759dd3aedf2	f05bb899-190f-40b0-b993-038e3011bf0b	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0038' deleted by Super Admin.	2026-10-31 12:07:47.483113+05:30
b033b01e-fcb7-4fe3-a2ba-0ea2ff47a89a	68bae788-12d3-40a8-97be-06ec36f8772e	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0036' deleted by Super Admin.	2026-10-31 12:07:50.067049+05:30
2f8750a8-0d43-4726-9f31-4898790cebc3	e32bf79c-e6e2-4615-b1f2-8040247c3f18	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0022' deleted by Super Admin.	2026-10-31 12:07:52.658268+05:30
3d11392b-5666-4a98-bbb1-c7771d885605	a939e2c4-35b9-47c9-9f8a-bc448c5bb877	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0021' deleted by Super Admin.	2026-10-31 12:07:56.549579+05:30
fa1209b7-2793-4aed-983b-8e223e33d080	4adf326f-6dda-4684-ab74-874667a59a0b	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0020' deleted by Super Admin.	2026-10-31 12:07:59.544928+05:30
49ec315c-3542-4433-b9d2-701e7030d7b1	da56b220-e470-4487-a407-48645b60dbdc	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0018' deleted by Super Admin.	2026-10-31 12:08:13.643257+05:30
118280ca-e62c-4e57-9204-7d7381e37f89	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	dcdee779-494b-4fe7-afa1-d3b66c784fbb	\N	Sales entry 'SO-2026-0017' deleted by Super Admin.	2026-10-31 12:08:16.495194+05:30
9cef8df9-d482-4779-bfe5-1d1f0f7768da	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	0438f197-65cc-4fb2-8667-bdaceee1db81	\N	Sales entry 'SO-2026-0016' deleted by Super Admin.	2026-10-31 12:08:18.874935+05:30
5df9207c-3639-407a-b1ed-160f16952848	dece3eea-3f5b-46f5-9d7c-29ad9334097c	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0015' deleted by Super Admin.	2026-10-31 12:08:21.379945+05:30
d647f66e-f79d-4f94-99a3-f4b45f79de86	0eef383e-ac4b-4541-a9a7-e0b98de5d548	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0014' deleted by Super Admin.	2026-10-31 12:08:23.87694+05:30
fdc90f65-8934-463c-8ad4-faab984e7965	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	Sales entry 'SO-2026-0013' deleted by Super Admin.	2026-10-31 12:08:28.590881+05:30
af4a8126-d876-4906-9e73-629b84ea1c8c	7b2791ff-c6bc-4ebe-9dbc-bec76ce3bdd5	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-11-01 18:41:07.574263+05:30
96fe72ca-5491-4952-8002-044b550e614f	4196c2a9-282c-40ee-8a75-2aebc5eef45d	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-11-01 18:42:14.777592+05:30
41b8d64d-8d66-4b71-9c63-f548156df039	3f2029b1-d446-46d9-960e-5ee9e676dd71	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-11-01 18:42:14.810223+05:30
b00971fa-7e5d-4b6f-a7c0-af8d0d357558	7f96f52b-ecc5-4172-a5e6-7018ebb135d7	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-11-01 18:42:14.834967+05:30
b5fc4b99-6558-40ef-8880-96f5eaa424f3	68d5f2f9-a3a6-469c-b790-6ff2f5da8529	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-11-01 18:42:14.855958+05:30
122e3d67-8d1b-465a-82ab-7e5d526f0125	342cb97c-953e-4643-bd89-7a2bd88ec2e8	de526836-5e73-49d7-9be3-8ad07caa6090	\N	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Initial task assignment on sales entry confirmation	2026-11-01 18:42:14.875774+05:30
320d16a1-1117-4f5d-933f-b819d36e1e58	342cb97c-953e-4643-bd89-7a2bd88ec2e8	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	65b43201-4875-4caa-a601-b0b535019b48	xcvfds	2026-11-02 18:36:14.450267+05:30
93b3d4c7-6da7-4d65-8797-f5fd871d08c2	7b2791ff-c6bc-4ebe-9dbc-bec76ce3bdd5	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0438f197-65cc-4fb2-8667-bdaceee1db81	asdfa	2026-11-02 18:36:38.2648+05:30
\.


--
-- Data for Name: application_document; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.application_document (app_doc_id, application_id, document_code, document_name, is_mandatory, status, rejection_reason, verified_by_user_id, verified_at, created_at, updated_at) FROM stdin;
0f5d913b-4525-46bd-8ca0-a4d98a074ab8	e1770a62-2997-4d34-9258-9300d62d5cbf	DOCTOR_DEGREE	Medical Council Registration & Degrees of Doctors	t	PENDING	\N	\N	\N	2026-09-23 23:42:54.314988+05:30	2026-09-23 23:42:54.314988+05:30
6392901b-9f25-4f9f-b4e4-f592ea0c710c	e1770a62-2997-4d34-9258-9300d62d5cbf	STAFF_DETAILS	Nursing and Paramedical Staff Credentials	t	PENDING	\N	\N	\N	2026-09-23 23:42:54.314988+05:30	2026-09-23 23:42:54.314988+05:30
555710d1-afa1-4294-b9a2-83acbac00d86	e1770a62-2997-4d34-9258-9300d62d5cbf	FIRE_NOC	Fire Department Safety NOC	t	PENDING	\N	\N	\N	2026-09-23 23:42:54.314988+05:30	2026-09-23 23:42:54.314988+05:30
98909c71-d0aa-46b8-99ac-0f2fe8a1b431	e1770a62-2997-4d34-9258-9300d62d5cbf	BM_WASTE	Bio-Medical Waste Management Agreement	t	PENDING	\N	\N	\N	2026-09-23 23:42:54.314988+05:30	2026-09-23 23:42:54.314988+05:30
66895a5c-7f19-4877-a306-3490e87d43c4	3ca55838-d953-4175-a37a-780ff438c869	PAN_MEMBER	PAN Card of Member and Nominee	t	PENDING	\N	\N	\N	2026-09-24 00:04:08.416007+05:30	2026-09-24 00:04:08.416007+05:30
d6d7a2a9-2e8a-4fcd-ac6d-e13588c0a66c	3ca55838-d953-4175-a37a-780ff438c869	NOMINEE_CONSENT	Form INC-3 Nominee Consent Letter	t	PENDING	\N	\N	\N	2026-09-24 00:04:08.416007+05:30	2026-09-24 00:04:08.416007+05:30
74f2d86d-cde5-410e-91b3-8489ef4cf3c4	3ca55838-d953-4175-a37a-780ff438c869	OFFICE_PROOF	Registered Office Utility Bill & NOC	t	PENDING	\N	\N	\N	2026-09-24 00:04:08.416007+05:30	2026-09-24 00:04:08.416007+05:30
ff5c1056-8f23-4031-a07a-2dab1436f51c	4ea8e868-36ad-4bf1-8faa-6ab242e954bd	PAN	PAN Card of Entity/Proprietor	t	PENDING	\N	\N	\N	2026-09-24 02:53:59.175861+05:30	2026-09-24 02:53:59.175861+05:30
2f45c432-0e52-4ee7-a9ce-f89918c334e6	4ea8e868-36ad-4bf1-8faa-6ab242e954bd	AADHAAR	Aadhaar Card of Applicant	t	PENDING	\N	\N	\N	2026-09-24 02:53:59.175861+05:30	2026-09-24 02:53:59.175861+05:30
c74588bb-43fc-40e4-8346-2c8fa817e99b	4ea8e868-36ad-4bf1-8faa-6ab242e954bd	RENT_AGREEMENT	Registered Rent Agreement / NOC	t	PENDING	\N	\N	\N	2026-09-24 02:53:59.175861+05:30	2026-09-24 02:53:59.175861+05:30
fcff668d-5fd1-41d8-b9ed-1888a0eb5e3a	4ea8e868-36ad-4bf1-8faa-6ab242e954bd	PROPERTY_TAX	Property Tax Receipt	t	PENDING	\N	\N	\N	2026-09-24 02:53:59.175861+05:30	2026-09-24 02:53:59.175861+05:30
ba4229e6-4353-47b9-aff9-e8d0f53b2914	4ea8e868-36ad-4bf1-8faa-6ab242e954bd	ELECTRICITY_BILL	Recent Electricity Bill	t	PENDING	\N	\N	\N	2026-09-24 02:53:59.175861+05:30	2026-09-24 02:53:59.175861+05:30
d82bbe44-bc19-4d04-b623-5c55a84fb4ef	3997d4d2-bfb5-4a06-8cec-929270aeb419	COI	Certificate of Incorporation	t	PENDING	\N	\N	\N	2026-09-24 02:54:54.6905+05:30	2026-09-24 02:54:54.6905+05:30
acd37fd5-a0fe-4de2-b52c-bfead1508ec8	3997d4d2-bfb5-4a06-8cec-929270aeb419	FORM_V	Form V issued by Principal Employer	t	PENDING	\N	\N	\N	2026-09-24 02:54:54.6905+05:30	2026-09-24 02:54:54.6905+05:30
e98733fb-ef3c-4061-88cc-b04902541b97	3997d4d2-bfb5-4a06-8cec-929270aeb419	PAN	Company PAN Card	t	PENDING	\N	\N	\N	2026-09-24 02:54:54.6905+05:30	2026-09-24 02:54:54.6905+05:30
2eb23a24-3b30-49e2-9c5b-1baf520d18f4	3997d4d2-bfb5-4a06-8cec-929270aeb419	AGREEMENT	Master Services Agreement with Principal Employer	t	PENDING	\N	\N	\N	2026-09-24 02:54:54.6905+05:30	2026-09-24 02:54:54.6905+05:30
09d9d6ad-e787-402b-a76d-8d6a9c623cdb	e78b8f08-be2e-4424-9799-6895e872e8c2	PAN_PARTNERS	PAN Cards of Designated Partners	t	PENDING	\N	\N	\N	2026-09-25 11:12:32.950864+05:30	2026-09-25 11:12:32.950864+05:30
1f0e1a3f-ae30-46dd-9771-a9dabd86cb23	e78b8f08-be2e-4424-9799-6895e872e8c2	ID_PROOF	Identity & Address Proofs of Partners	t	PENDING	\N	\N	\N	2026-09-25 11:12:32.950864+05:30	2026-09-25 11:12:32.950864+05:30
5d8d848e-b674-49d6-aa9a-c069dc8fb838	e78b8f08-be2e-4424-9799-6895e872e8c2	OFFICE_PROOF	Registered Office Address Proof & NOC	t	PENDING	\N	\N	\N	2026-09-25 11:12:32.950864+05:30	2026-09-25 11:12:32.950864+05:30
2debfc64-176f-4369-a7b6-78685e937827	e78b8f08-be2e-4424-9799-6895e872e8c2	LLP_AGREEMENT	Executed LLP Agreement	t	PENDING	\N	\N	\N	2026-09-25 11:12:32.950864+05:30	2026-09-25 11:12:32.950864+05:30
f675d522-75c4-481e-bd08-e835a73f57e1	51d9ae10-f22d-448f-a560-c2a9323ffea8	DOCTOR_DEGREE	Medical Council Registration & Degrees of Doctors	t	PENDING	\N	\N	\N	2026-09-25 14:04:23.568611+05:30	2026-09-25 14:04:23.568611+05:30
f0c9a083-fde4-4460-90b1-bc1bd89f3ae0	51d9ae10-f22d-448f-a560-c2a9323ffea8	STAFF_DETAILS	Nursing and Paramedical Staff Credentials	t	PENDING	\N	\N	\N	2026-09-25 14:04:23.568611+05:30	2026-09-25 14:04:23.568611+05:30
979b9916-f672-41cf-9efd-e68f1df23543	51d9ae10-f22d-448f-a560-c2a9323ffea8	FIRE_NOC	Fire Department Safety NOC	t	PENDING	\N	\N	\N	2026-09-25 14:04:23.568611+05:30	2026-09-25 14:04:23.568611+05:30
b999cfbd-d58f-405e-accc-fe2e2c8bf462	51d9ae10-f22d-448f-a560-c2a9323ffea8	BM_WASTE	Bio-Medical Waste Management Agreement	t	PENDING	\N	\N	\N	2026-09-25 14:04:23.568611+05:30	2026-09-25 14:04:23.568611+05:30
0209947c-8d89-4971-bdf6-a8d5f6a0fa72	6bccf11d-68fe-4020-bac4-820936578bec	EXPLOSIVE_PLAN	Approved Storage and Handling Blueprint	t	PENDING	\N	\N	\N	2026-09-25 14:06:06.490372+05:30	2026-09-25 14:06:06.490372+05:30
d4dc4230-fe09-4fae-875c-c905504475ae	6bccf11d-68fe-4020-bac4-820936578bec	SAFETY_CERT	Competent Person Safety & Fabricator Certificate	t	PENDING	\N	\N	\N	2026-09-25 14:06:06.490372+05:30	2026-09-25 14:06:06.490372+05:30
c862c842-1603-4a76-bae5-ba16fb5a03b8	6bccf11d-68fe-4020-bac4-820936578bec	DM_NOC	District Magistrate No Objection Certificate	t	PENDING	\N	\N	\N	2026-09-25 14:06:06.490372+05:30	2026-09-25 14:06:06.490372+05:30
3bc0fbe2-1fd2-4225-a280-038d61608937	6bccf11d-68fe-4020-bac4-820936578bec	COI	Corporate Entity Incorporation Proof	t	PENDING	\N	\N	\N	2026-09-25 14:06:06.490372+05:30	2026-09-25 14:06:06.490372+05:30
762f5f74-348e-494c-b275-de24a5d50040	db093cfd-6c3b-473c-ae66-9b295924aa36	EXPLOSIVE_PLAN	Approved Storage and Handling Blueprint	t	PENDING	\N	\N	\N	2026-09-28 15:55:03.197591+05:30	2026-09-28 15:55:03.197591+05:30
aee06f76-dedf-4546-880f-17d717d7720c	db093cfd-6c3b-473c-ae66-9b295924aa36	SAFETY_CERT	Competent Person Safety & Fabricator Certificate	t	PENDING	\N	\N	\N	2026-09-28 15:55:03.197591+05:30	2026-09-28 15:55:03.197591+05:30
2f864f6a-5b75-4e6f-b653-d599dd559401	db093cfd-6c3b-473c-ae66-9b295924aa36	DM_NOC	District Magistrate No Objection Certificate	t	PENDING	\N	\N	\N	2026-09-28 15:55:03.197591+05:30	2026-09-28 15:55:03.197591+05:30
404d2249-e600-4ad3-8529-4fc5fa6dd108	db093cfd-6c3b-473c-ae66-9b295924aa36	COI	Corporate Entity Incorporation Proof	t	PENDING	\N	\N	\N	2026-09-28 15:55:03.197591+05:30	2026-09-28 15:55:03.197591+05:30
7445b0a8-c6d4-442a-937e-2a2ae49abd4f	058b6bc8-9285-43fd-8c52-67532eb40ac6	PAN	PAN Card of Business Owner	t	PENDING	\N	\N	\N	2026-09-28 15:57:17.610013+05:30	2026-09-28 15:57:17.610013+05:30
3e61ab80-dd24-4049-b5a0-45d5654be023	058b6bc8-9285-43fd-8c52-67532eb40ac6	AADHAAR	Aadhaar Card of Authorized Person	t	PENDING	\N	\N	\N	2026-09-28 15:57:17.610013+05:30	2026-09-28 15:57:17.610013+05:30
96e4fd58-4be2-4fa3-aa5b-c7c907f62733	058b6bc8-9285-43fd-8c52-67532eb40ac6	GEO_IMAGE	Geo-tagged photo of shop with signboard	t	PENDING	\N	\N	\N	2026-09-28 15:57:17.610013+05:30	2026-09-28 15:57:17.610013+05:30
ccc8bb44-fe9a-40f7-a505-cbb55185a0e2	058b6bc8-9285-43fd-8c52-67532eb40ac6	RENT_AGREEMENT	Rent Agreement / Ownership Proof	t	PENDING	\N	\N	\N	2026-09-28 15:57:17.610013+05:30	2026-09-28 15:57:17.610013+05:30
56cbc285-ceb5-44c0-9bd1-4d54aa44bb5e	e0a66aa9-91bf-4214-85e2-5d8e270f2b23	COI	Certificate of Incorporation	t	PENDING	\N	\N	\N	2026-09-28 15:58:28.190352+05:30	2026-09-28 15:58:28.190352+05:30
ed3d8117-e551-4b0b-b1ff-f58ef70077c7	e0a66aa9-91bf-4214-85e2-5d8e270f2b23	FORM_V	Form V issued by Principal Employer	t	PENDING	\N	\N	\N	2026-09-28 15:58:28.190352+05:30	2026-09-28 15:58:28.190352+05:30
eedae49b-791a-4a7f-aabf-d1a3d318b13f	e0a66aa9-91bf-4214-85e2-5d8e270f2b23	PAN	Company PAN Card	t	PENDING	\N	\N	\N	2026-09-28 15:58:28.190352+05:30	2026-09-28 15:58:28.190352+05:30
3ec4ae8a-9a99-48ca-a98c-754ae633c553	e0a66aa9-91bf-4214-85e2-5d8e270f2b23	AGREEMENT	Master Services Agreement with Principal Employer	t	PENDING	\N	\N	\N	2026-09-28 15:58:28.190352+05:30	2026-09-28 15:58:28.190352+05:30
824bc600-1a8a-461f-bded-28a02a8a45dc	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	EXPLOSIVE_PLAN	Approved Storage and Handling Blueprint	t	PENDING	\N	\N	\N	2026-09-29 16:53:39.808136+05:30	2026-09-29 16:53:39.808136+05:30
5321040e-b298-4e37-b68d-e61d28fc13ed	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	SAFETY_CERT	Competent Person Safety & Fabricator Certificate	t	PENDING	\N	\N	\N	2026-09-29 16:53:39.808136+05:30	2026-09-29 16:53:39.808136+05:30
123185cf-7e49-453b-bd13-3e30540b7c0c	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	DM_NOC	District Magistrate No Objection Certificate	t	PENDING	\N	\N	\N	2026-09-29 16:53:39.808136+05:30	2026-09-29 16:53:39.808136+05:30
61acad32-ce41-4a13-a2b7-6354aefc8284	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	COI	Corporate Entity Incorporation Proof	t	PENDING	\N	\N	\N	2026-09-29 16:53:39.808136+05:30	2026-09-29 16:53:39.808136+05:30
114b4600-9670-434b-bb9a-4e641bc3be41	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	DOCTOR_DEGREE	Medical Council Registration & Degrees of Doctors	t	PENDING	\N	\N	\N	2026-09-30 11:16:20.182113+05:30	2026-09-30 11:16:20.182113+05:30
2cc6a92a-e90c-43aa-88c5-5998bb585154	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	STAFF_DETAILS	Nursing and Paramedical Staff Credentials	t	PENDING	\N	\N	\N	2026-09-30 11:16:20.182113+05:30	2026-09-30 11:16:20.182113+05:30
6bed4e4e-438f-4ac7-93b6-7ddcd1e7c27a	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	FIRE_NOC	Fire Department Safety NOC	t	PENDING	\N	\N	\N	2026-09-30 11:16:20.182113+05:30	2026-09-30 11:16:20.182113+05:30
f6eba960-b617-4486-b779-11b842a9f5bc	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	BM_WASTE	Bio-Medical Waste Management Agreement	t	PENDING	\N	\N	\N	2026-09-30 11:16:20.182113+05:30	2026-09-30 11:16:20.182113+05:30
29001ed4-051e-4ffd-b108-786e4a5564ab	0eef383e-ac4b-4541-a9a7-e0b98de5d548	DOCTOR_DEGREE	Medical Council Registration & Degrees of Doctors	t	PENDING	\N	\N	\N	2026-10-07 01:33:04.422815+05:30	2026-10-07 01:33:04.422815+05:30
63cb0143-05d7-496b-809d-ade377c3aa4d	0eef383e-ac4b-4541-a9a7-e0b98de5d548	STAFF_DETAILS	Nursing and Paramedical Staff Credentials	t	PENDING	\N	\N	\N	2026-10-07 01:33:04.422815+05:30	2026-10-07 01:33:04.422815+05:30
8a453b95-7a3c-42b9-a4e5-a65260a67f1c	0eef383e-ac4b-4541-a9a7-e0b98de5d548	FIRE_NOC	Fire Department Safety NOC	t	PENDING	\N	\N	\N	2026-10-07 01:33:04.422815+05:30	2026-10-07 01:33:04.422815+05:30
9765471b-c4df-4631-9921-0cc9b2e112d9	0eef383e-ac4b-4541-a9a7-e0b98de5d548	BM_WASTE	Bio-Medical Waste Management Agreement	t	PENDING	\N	\N	\N	2026-10-07 01:33:04.422815+05:30	2026-10-07 01:33:04.422815+05:30
65cbfae4-de5e-4c20-b716-27ebd53de345	dece3eea-3f5b-46f5-9d7c-29ad9334097c	EXPLOSIVE_PLAN	Approved Storage and Handling Blueprint	t	PENDING	\N	\N	\N	2026-10-07 01:33:59.33512+05:30	2026-10-07 01:33:59.33512+05:30
e09a60ac-fb4c-4205-a220-c0dcde384d58	dece3eea-3f5b-46f5-9d7c-29ad9334097c	SAFETY_CERT	Competent Person Safety & Fabricator Certificate	t	PENDING	\N	\N	\N	2026-10-07 01:33:59.33512+05:30	2026-10-07 01:33:59.33512+05:30
1a92b2de-601c-411d-87a8-fc1290b116e9	dece3eea-3f5b-46f5-9d7c-29ad9334097c	DM_NOC	District Magistrate No Objection Certificate	t	PENDING	\N	\N	\N	2026-10-07 01:33:59.33512+05:30	2026-10-07 01:33:59.33512+05:30
a2129cea-dbfd-4961-a31c-ce2f73fb5ea6	dece3eea-3f5b-46f5-9d7c-29ad9334097c	COI	Corporate Entity Incorporation Proof	t	PENDING	\N	\N	\N	2026-10-07 01:33:59.33512+05:30	2026-10-07 01:33:59.33512+05:30
59bb2419-7466-49da-aa43-22acc788766e	da56b220-e470-4487-a407-48645b60dbdc	DOCTOR_DEGREE	Medical Council Registration & Degrees of Doctors	t	PENDING	\N	\N	\N	2026-10-09 19:27:56.209419+05:30	2026-10-09 19:27:56.209419+05:30
4ea7e7c9-5891-4190-b1ee-ac79901654ce	da56b220-e470-4487-a407-48645b60dbdc	STAFF_DETAILS	Nursing and Paramedical Staff Credentials	t	PENDING	\N	\N	\N	2026-10-09 19:27:56.209419+05:30	2026-10-09 19:27:56.209419+05:30
133e041c-5406-4ebf-a733-60288393367b	da56b220-e470-4487-a407-48645b60dbdc	FIRE_NOC	Fire Department Safety NOC	t	PENDING	\N	\N	\N	2026-10-09 19:27:56.209419+05:30	2026-10-09 19:27:56.209419+05:30
1cba4887-a0d5-47cb-8cb4-19a412b1b15f	da56b220-e470-4487-a407-48645b60dbdc	BM_WASTE	Bio-Medical Waste Management Agreement	t	PENDING	\N	\N	\N	2026-10-09 19:27:56.209419+05:30	2026-10-09 19:27:56.209419+05:30
fba10a87-ef17-4f87-824f-88710654f6ab	4adf326f-6dda-4684-ab74-874667a59a0b	DOCTOR_DEGREE	Medical Council Registration & Degrees of Doctors	t	PENDING	\N	\N	\N	2026-10-24 22:55:03.17085+05:30	2026-10-24 22:55:03.17085+05:30
13797b76-27ff-463c-8626-bef5d0b196d4	4adf326f-6dda-4684-ab74-874667a59a0b	STAFF_DETAILS	Nursing and Paramedical Staff Credentials	t	PENDING	\N	\N	\N	2026-10-24 22:55:03.17085+05:30	2026-10-24 22:55:03.17085+05:30
6a08b58b-df5b-4d7c-ac52-e58255b2e130	4adf326f-6dda-4684-ab74-874667a59a0b	FIRE_NOC	Fire Department Safety NOC	t	PENDING	\N	\N	\N	2026-10-24 22:55:03.17085+05:30	2026-10-24 22:55:03.17085+05:30
c490a0cf-452c-471a-a4ae-4b9d4036b9f8	4adf326f-6dda-4684-ab74-874667a59a0b	BM_WASTE	Bio-Medical Waste Management Agreement	t	PENDING	\N	\N	\N	2026-10-24 22:55:03.17085+05:30	2026-10-24 22:55:03.17085+05:30
0ffb4b71-031f-4b0e-bb66-25ea30780c6c	a939e2c4-35b9-47c9-9f8a-bc448c5bb877	DOCTOR_DEGREE	Medical Council Registration & Degrees of Doctors	t	PENDING	\N	\N	\N	2026-10-24 22:56:52.733047+05:30	2026-10-24 22:56:52.733047+05:30
9b2f13d9-e3aa-4b7a-86f4-f4891401985d	a939e2c4-35b9-47c9-9f8a-bc448c5bb877	STAFF_DETAILS	Nursing and Paramedical Staff Credentials	t	PENDING	\N	\N	\N	2026-10-24 22:56:52.733047+05:30	2026-10-24 22:56:52.733047+05:30
e67447ff-1b50-4df1-a928-d87de5768725	a939e2c4-35b9-47c9-9f8a-bc448c5bb877	FIRE_NOC	Fire Department Safety NOC	t	PENDING	\N	\N	\N	2026-10-24 22:56:52.733047+05:30	2026-10-24 22:56:52.733047+05:30
df1f271a-f479-4946-97a7-791d7a82afed	a939e2c4-35b9-47c9-9f8a-bc448c5bb877	BM_WASTE	Bio-Medical Waste Management Agreement	t	PENDING	\N	\N	\N	2026-10-24 22:56:52.733047+05:30	2026-10-24 22:56:52.733047+05:30
105de1f7-5b30-4be3-90db-5b990de03cd3	8553d61d-cce7-4877-8474-9a990c4ee4ec	COI	Certificate of Incorporation	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
fea450b3-4a6b-4a97-a6f4-280f672003cb	8553d61d-cce7-4877-8474-9a990c4ee4ec	FORM_V	Form V issued by Principal Employer	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
c129f9d0-c771-4541-8e01-22a24994f960	8553d61d-cce7-4877-8474-9a990c4ee4ec	PAN	Company PAN Card	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
a5121ad1-2c80-4b1b-8d08-284f81be7096	8553d61d-cce7-4877-8474-9a990c4ee4ec	AGREEMENT	Master Services Agreement with Principal Employer	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
14af4b8e-1237-462a-adc1-9216bed6a1e3	950cc940-dbb1-45e3-a4fc-276eced83899	PAN	PAN Card of Business Owner	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
1ca640c9-e95f-47df-9ce9-fa998f47f4a0	950cc940-dbb1-45e3-a4fc-276eced83899	AADHAAR	Aadhaar Card of Authorized Person	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
31bed3eb-7374-40a7-8bf4-6b6d774295e5	950cc940-dbb1-45e3-a4fc-276eced83899	GEO_IMAGE	Geo-tagged photo of shop with signboard	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
e683bb43-73c6-46ba-885e-78b67b3a9bb6	950cc940-dbb1-45e3-a4fc-276eced83899	RENT_AGREEMENT	Rent Agreement / Ownership Proof	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
d9ec0b9a-b0bc-48b8-84ac-86a17545d3c6	2f3b7575-2066-493a-a62c-fc95be74d0fb	SITE_PLAN	Site Layout and Plant Machinery Plan	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
95a652fd-89c5-476e-83b5-4c5083552e2e	2f3b7575-2066-493a-a62c-fc95be74d0fb	PROJECT_REPORT	Detailed Project Report on Emissions/Effluents	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
b205b1cc-d2be-4951-a558-13b2d81d5da4	2f3b7575-2066-493a-a62c-fc95be74d0fb	LAND_DOCS	Land Possession / Ownership Documents	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
9b10dcb0-4240-4f15-821e-73cc1a34d906	2f3b7575-2066-493a-a62c-fc95be74d0fb	COI	Certificate of Incorporation / Registration	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
dcf77143-6230-4b75-b400-f4661b3e2a3c	2f3b7575-2066-493a-a62c-fc95be74d0fb	WATER_NOC	Water Connection NOC / Supply Bill	f	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
c83a643a-67f9-4726-9735-aac4d55917b6	eaeea2ed-76f7-4b5a-a5be-a9f304b72275	PAN_PARTNERS	PAN Cards of Designated Partners	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
e71eae3f-e1fd-4b55-b1c7-89b1947864ee	eaeea2ed-76f7-4b5a-a5be-a9f304b72275	ID_PROOF	Identity & Address Proofs of Partners	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
10814bb5-e9a3-41af-87be-0b8bf0ede7e2	eaeea2ed-76f7-4b5a-a5be-a9f304b72275	OFFICE_PROOF	Registered Office Address Proof & NOC	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
bf50aa9a-dbdb-4428-b98a-26a5e82ebf07	eaeea2ed-76f7-4b5a-a5be-a9f304b72275	LLP_AGREEMENT	Executed LLP Agreement	t	PENDING	\N	\N	\N	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
07dc131c-2d31-4495-bef9-bc6f72a4c155	680e84cc-4054-49d2-b147-d6a86b5b9a13	COI	Certificate of Incorporation	t	PENDING	\N	\N	\N	2026-10-25 23:04:54.377324+05:30	2026-10-25 23:04:54.377324+05:30
043a2c99-958d-4b14-a232-de1faf05b136	680e84cc-4054-49d2-b147-d6a86b5b9a13	FORM_V	Form V issued by Principal Employer	t	PENDING	\N	\N	\N	2026-10-25 23:04:54.377324+05:30	2026-10-25 23:04:54.377324+05:30
1ed8a0f9-a4d0-4397-a811-7622efd5faa6	680e84cc-4054-49d2-b147-d6a86b5b9a13	PAN	Company PAN Card	t	PENDING	\N	\N	\N	2026-10-25 23:04:54.377324+05:30	2026-10-25 23:04:54.377324+05:30
39dd727b-b7ce-492b-a695-2efa2441b053	680e84cc-4054-49d2-b147-d6a86b5b9a13	AGREEMENT	Master Services Agreement with Principal Employer	t	PENDING	\N	\N	\N	2026-10-25 23:04:54.377324+05:30	2026-10-25 23:04:54.377324+05:30
af2745a9-4d4a-4b67-879f-def087532bc6	ca0c550f-6f0e-4b06-8466-66fc8b221831	COI	Certificate of Incorporation	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
26d2608f-834f-472c-b162-0eb3b764bea3	ca0c550f-6f0e-4b06-8466-66fc8b221831	FORM_V	Form V issued by Principal Employer	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
b06a794c-163f-4b9d-87d1-f4be2988437d	ca0c550f-6f0e-4b06-8466-66fc8b221831	PAN	Company PAN Card	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
6f2b1dde-68e1-49f5-8b11-0a9a48e4f91f	ca0c550f-6f0e-4b06-8466-66fc8b221831	AGREEMENT	Master Services Agreement with Principal Employer	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
07a21512-84ae-492b-b967-2446071db57f	733b35e2-4330-4588-aa1f-5ec8d6df279c	PAN	PAN Card of Business Owner	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
a4b385d7-299d-4645-b7d5-9e8bd7f1935c	733b35e2-4330-4588-aa1f-5ec8d6df279c	AADHAAR	Aadhaar Card of Authorized Person	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
f8db3d27-1574-4978-a8ff-a4a22eb2c671	733b35e2-4330-4588-aa1f-5ec8d6df279c	GEO_IMAGE	Geo-tagged photo of shop with signboard	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
5e5fcc00-6d3d-44a6-a46b-1744a7092a46	733b35e2-4330-4588-aa1f-5ec8d6df279c	RENT_AGREEMENT	Rent Agreement / Ownership Proof	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
1b8cc1db-6460-452c-a9b4-3a90e6580ddc	5975e799-fb23-4f30-8f31-4338ed37ee4a	SITE_PLAN	Site Layout and Plant Machinery Plan	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
f17ee7be-c481-4eba-a248-ba4de709619d	5975e799-fb23-4f30-8f31-4338ed37ee4a	PROJECT_REPORT	Detailed Project Report on Emissions/Effluents	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
858c6dfe-f258-4324-8751-7637d21cd134	5975e799-fb23-4f30-8f31-4338ed37ee4a	LAND_DOCS	Land Possession / Ownership Documents	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
da1fd85a-8084-4ebd-b799-afff8eed2c86	5975e799-fb23-4f30-8f31-4338ed37ee4a	COI	Certificate of Incorporation / Registration	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
14570470-93a2-4ccd-b1d4-e72686245d27	5975e799-fb23-4f30-8f31-4338ed37ee4a	WATER_NOC	Water Connection NOC / Supply Bill	f	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
5aaecc3c-c87f-4c37-9ca3-0cb5257b9e98	2bed4f2b-61f3-45b0-bf20-474a212be9e3	COI	Certificate of Incorporation	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
bb87a4cd-01fd-4bc8-89bc-0105efd70d09	2bed4f2b-61f3-45b0-bf20-474a212be9e3	FORM_V	Form V issued by Principal Employer	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
18a2fc46-f0c1-455f-9ddb-d5a7c9dcceea	2bed4f2b-61f3-45b0-bf20-474a212be9e3	PAN	Company PAN Card	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
5111578a-2ecd-4a6f-b666-0f888df2b1ce	2bed4f2b-61f3-45b0-bf20-474a212be9e3	AGREEMENT	Master Services Agreement with Principal Employer	t	PENDING	\N	\N	\N	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:37:35.72326+05:30
2d0d6568-291c-41f9-9949-50f96f175700	2df25880-1b91-4ed4-9eb4-9aa54cb56f53	COI	Certificate of Incorporation	t	PENDING	\N	\N	\N	2026-10-25 23:48:24.453326+05:30	2026-10-25 23:48:24.453326+05:30
49a1780a-a88c-4367-acb4-bae60419f9fd	2df25880-1b91-4ed4-9eb4-9aa54cb56f53	FORM_V	Form V issued by Principal Employer	t	PENDING	\N	\N	\N	2026-10-25 23:48:24.453326+05:30	2026-10-25 23:48:24.453326+05:30
55e7001e-03ea-44d6-b106-adda8099164a	2df25880-1b91-4ed4-9eb4-9aa54cb56f53	PAN	Company PAN Card	t	PENDING	\N	\N	\N	2026-10-25 23:48:24.453326+05:30	2026-10-25 23:48:24.453326+05:30
35046e15-138a-42fe-bb93-90563d8e6a81	2df25880-1b91-4ed4-9eb4-9aa54cb56f53	AGREEMENT	Master Services Agreement with Principal Employer	t	PENDING	\N	\N	\N	2026-10-25 23:48:24.453326+05:30	2026-10-25 23:48:24.453326+05:30
721d101d-f0e7-4cb2-941f-6493c1cea9c9	f25069b3-5013-4ebb-82ef-cea01267657c	COI	Certificate of Incorporation	t	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
5a183885-71ef-4a98-9242-8bc8319aba56	f25069b3-5013-4ebb-82ef-cea01267657c	FORM_V	Form V issued by Principal Employer	t	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
93c1ee63-fa4d-4874-8ca4-f34b642ea57e	f25069b3-5013-4ebb-82ef-cea01267657c	PAN	Company PAN Card	t	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
b1f5476e-0b97-4b23-afaf-3e377847ac8a	f25069b3-5013-4ebb-82ef-cea01267657c	AGREEMENT	Master Services Agreement with Principal Employer	t	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
0372a347-8dc7-4540-b9dd-5d2d3ae11630	68bae788-12d3-40a8-97be-06ec36f8772e	PAN	PAN Card of Business Owner	t	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
0a7dde11-c5a4-4a6c-8065-e543f51ab7cf	68bae788-12d3-40a8-97be-06ec36f8772e	AADHAAR	Aadhaar Card of Authorized Person	t	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
daa82f38-2255-43cc-8e05-96c0fef89a32	68bae788-12d3-40a8-97be-06ec36f8772e	GEO_IMAGE	Geo-tagged photo of shop with signboard	t	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
84a58447-f8b0-4e5c-b46b-5cac5d866cd6	68bae788-12d3-40a8-97be-06ec36f8772e	RENT_AGREEMENT	Rent Agreement / Ownership Proof	t	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
4c720d11-a6cf-40a2-a009-5674f79b8adb	f05bb899-190f-40b0-b993-038e3011bf0b	SITE_PLAN	Site Layout and Plant Machinery Plan	t	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
b064cb21-25d9-40f4-8d78-24838e6a9e52	f05bb899-190f-40b0-b993-038e3011bf0b	PROJECT_REPORT	Detailed Project Report on Emissions/Effluents	t	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
acdc35ed-4cca-487c-9a4f-80fbad3cd286	f05bb899-190f-40b0-b993-038e3011bf0b	LAND_DOCS	Land Possession / Ownership Documents	t	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
b50c8dbd-8bcf-4437-8f91-8aa82b8af7ee	f05bb899-190f-40b0-b993-038e3011bf0b	COI	Certificate of Incorporation / Registration	t	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
cdbda245-55f1-47af-8ccd-50161d897a6f	f05bb899-190f-40b0-b993-038e3011bf0b	WATER_NOC	Water Connection NOC / Supply Bill	f	PENDING	\N	\N	\N	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:08:10.110917+05:30
043988a8-d788-420f-b3ab-3f511fe2da3f	7b2791ff-c6bc-4ebe-9dbc-bec76ce3bdd5	COI	Certificate of Incorporation	t	PENDING	\N	\N	\N	2026-11-01 18:41:07.525029+05:30	2026-11-01 18:41:07.525029+05:30
73a30348-7611-40bf-ac84-8e74c99315a4	7b2791ff-c6bc-4ebe-9dbc-bec76ce3bdd5	FORM_V	Form V issued by Principal Employer	t	PENDING	\N	\N	\N	2026-11-01 18:41:07.525029+05:30	2026-11-01 18:41:07.525029+05:30
c51fdaa8-7960-49b5-b031-ba6dbe596ddf	7b2791ff-c6bc-4ebe-9dbc-bec76ce3bdd5	PAN	Company PAN Card	t	PENDING	\N	\N	\N	2026-11-01 18:41:07.525029+05:30	2026-11-01 18:41:07.525029+05:30
8fbdcafd-4331-450d-9930-9e4580bfefe8	7b2791ff-c6bc-4ebe-9dbc-bec76ce3bdd5	AGREEMENT	Master Services Agreement with Principal Employer	t	PENDING	\N	\N	\N	2026-11-01 18:41:07.525029+05:30	2026-11-01 18:41:07.525029+05:30
3e4fff4d-064e-4ef0-b17f-8598f1eef80b	4196c2a9-282c-40ee-8a75-2aebc5eef45d	COI	Certificate of Incorporation	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
97db3d61-8c61-44ae-8d9b-b8de3dfcf578	4196c2a9-282c-40ee-8a75-2aebc5eef45d	FORM_V	Form V issued by Principal Employer	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
8e636579-a3ad-4518-b74c-8f6499d86018	4196c2a9-282c-40ee-8a75-2aebc5eef45d	PAN	Company PAN Card	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
5157bdf1-9ae3-48c7-8c34-b67b0e73cf30	4196c2a9-282c-40ee-8a75-2aebc5eef45d	AGREEMENT	Master Services Agreement with Principal Employer	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
61591286-1a8b-48bd-a8d5-029ed758f73e	3f2029b1-d446-46d9-960e-5ee9e676dd71	PAN	PAN Card of Business Owner	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
bf19d883-48fd-4944-8c83-a8a7df03081c	3f2029b1-d446-46d9-960e-5ee9e676dd71	AADHAAR	Aadhaar Card of Authorized Person	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
97522f8d-09f8-48ac-be96-9ac7070189b1	3f2029b1-d446-46d9-960e-5ee9e676dd71	GEO_IMAGE	Geo-tagged photo of shop with signboard	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
547ba146-e7f9-4942-8adb-950bbaa383cd	3f2029b1-d446-46d9-960e-5ee9e676dd71	RENT_AGREEMENT	Rent Agreement / Ownership Proof	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
7365bb22-2276-4a66-ab2e-a0309ef37c8b	7f96f52b-ecc5-4172-a5e6-7018ebb135d7	COI	Certificate of Incorporation	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
a9dc8f43-68c8-4bfc-a1b7-6bc1a4971553	7f96f52b-ecc5-4172-a5e6-7018ebb135d7	FORM_V	Form V issued by Principal Employer	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
59b25c8d-c6da-46f5-8de4-f705c8f36358	7f96f52b-ecc5-4172-a5e6-7018ebb135d7	PAN	Company PAN Card	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
fe114596-8005-4a97-a799-0759123e7f57	7f96f52b-ecc5-4172-a5e6-7018ebb135d7	AGREEMENT	Master Services Agreement with Principal Employer	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
d567bac4-588f-4f4e-bac5-79ab7c7b534d	68d5f2f9-a3a6-469c-b790-6ff2f5da8529	SITE_PLAN	Site Layout and Plant Machinery Plan	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
94d5d86a-b80a-4a72-b379-4058a0e7b0f8	68d5f2f9-a3a6-469c-b790-6ff2f5da8529	PROJECT_REPORT	Detailed Project Report on Emissions/Effluents	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
446a7b71-7bfd-4032-b938-387c3e10747a	68d5f2f9-a3a6-469c-b790-6ff2f5da8529	LAND_DOCS	Land Possession / Ownership Documents	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
26eb498a-fa90-480a-b9f9-6f4779fcebb8	68d5f2f9-a3a6-469c-b790-6ff2f5da8529	COI	Certificate of Incorporation / Registration	t	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
2f020e11-eabb-478b-9846-306777ac5885	68d5f2f9-a3a6-469c-b790-6ff2f5da8529	WATER_NOC	Water Connection NOC / Supply Bill	f	PENDING	\N	\N	\N	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30
\.


--
-- Data for Name: auth_refresh_token; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.auth_refresh_token (refresh_token_id, user_id, jti, token_hash, issued_at, expires_at, revoked_at, replaced_by_jti, created_ip, user_agent) FROM stdin;
15ead904-71f7-4e62-b430-7c6387ddb9e5	de526836-5e73-49d7-9be3-8ad07caa6090	c0addb66860f5e454db882fbdef415072cc544ee8a1bc197a109018f31ce2eb7	9d3100b4c2ed05a9e4be43d16ceb8e16095985e209b5541f0589179837ab1fcd	2026-09-21 00:08:28.296905+05:30	2026-09-28 00:08:28.355478+05:30	2026-09-21 00:13:17.426918+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
e2259c32-7ca3-4708-a05f-e202baa9ef86	de526836-5e73-49d7-9be3-8ad07caa6090	e714b83b81cf7c6c4590c407d1fae29d9f18e5e01cc054e265b210f2c353c25f	05cfe802bffdbdd3e96d0a4cea31dc65d0b8d3ff1cbefb1904a7fc170e2cb5de	2026-09-29 16:50:19.528215+05:30	2026-10-29 16:50:19.581301+05:30	2026-09-30 10:48:10.485795+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
5e2ddd87-fdf5-4a0c-8b80-3841ff3e8717	de526836-5e73-49d7-9be3-8ad07caa6090	baa183299d90173d4a27aa09f739a59b4dc5e08009a0720e924259e96516b8a0	eb140d1bf7ffcb7b76fd6bce87bb2dfb6623fdd0ee937326fe83b461ae6a375a	2026-09-21 02:08:59.788242+05:30	2026-09-28 02:08:59.858084+05:30	2026-09-21 02:16:36.602599+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
18748d74-e9d1-4fca-92fe-d7c9de768f0c	de526836-5e73-49d7-9be3-8ad07caa6090	cfc498c42f5c8a5b18faf5b7a655de606fbe727577d766ad4e87f7d0bda6d147	27991375c2989f7b15c5ba11a550166dcf5fd815519dfa22b2236bea0d7b1ac1	2026-09-21 00:54:42.412935+05:30	2026-09-28 00:54:42.471405+05:30	2026-09-21 00:56:07.392762+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
c5f11b54-51ba-4442-935d-7227227ab2c7	de526836-5e73-49d7-9be3-8ad07caa6090	67cd0dbefa7e1fc7d8627fb30930af70bba48d692df93b22aaba9e224bf0f458	8cef8afdd3bf6ae1b2f2bc19d50ea12f77454e00af3a36a780b26d81b7d7225a	2026-10-06 23:16:38.028394+05:30	2026-11-05 23:16:38.10698+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
a2176aca-abe3-4bcd-a23b-6103de7ebfab	de526836-5e73-49d7-9be3-8ad07caa6090	ceab0efb03f9df2590ba82dc48f516f52893096370d70060b04bd4510f7b795e	420d4d5c095f0e46ac2391ff41256b4d326b68d2e73df0db106a19800e2caffb	2026-09-30 10:48:12.119923+05:30	2026-10-30 10:48:12.194213+05:30	2026-10-09 10:51:22.958624+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
203faf09-bade-4b6b-a0de-0fac7761a10c	de526836-5e73-49d7-9be3-8ad07caa6090	e40ac86c056fac47546ff475c9565e53152d46b0105a888f3bb93da0561db4f1	d8bd491aacb1f68b76b8321de3ff987204012cc39beaf554c9ecf34b4af4d02d	2026-09-21 02:17:17.760545+05:30	2026-09-28 02:17:17.841204+05:30	2026-09-21 02:17:25.071452+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
53c5492c-3b1c-43f6-9d9c-741603899bf0	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	1a8093e0fe6059250b191ecde5a623f8fb3280158148bc55e4dd6b39ab258ddf	6adb0842164955cabd8e6b7e27ef94534ab0fe1ca09463c1726eb2b04a7b5e1e	2026-09-21 23:42:55.881462+05:30	2026-09-28 23:42:55.976999+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
50fe98cb-3613-45c7-9f19-a398d8e032e3	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	e3122de3e5629248c11468e0ba4ac9424231ecc714ec747a75191d505b132e91	a9115d43259875f66f0d1dc69ef70f3218cbfcc02244f9c55c6f42a584986116	2026-09-22 01:14:40.127435+05:30	2026-09-29 01:14:40.22378+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
6cc143b0-f35e-4641-bf42-cc48f0ba7133	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	589451d66660051e221ec8784095ec6e998e14db2e3cdac80d787ae212afdaa9	992829c3354e75d58f7cbdc0432d559831fccfc9e84eca97f8b82cfebd378fcc	2026-09-22 02:02:13.358316+05:30	2026-09-29 02:02:13.428588+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
b5701bb3-f46d-4c58-8b15-957122dfc3d2	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	3ccffb0141d9c3f62be623ef8fe573323146420702954dc2a77b92c91d6ae3cf	9afb13896e895a426101947fbc5e0b574d613800b4b5929bef1f604a3ff43d32	2026-10-09 10:51:37.520061+05:30	2026-11-08 10:51:37.620953+05:30	2026-10-09 19:13:30.929882+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
200e5bb8-1515-4cfe-9ea9-2047380cfe4b	de526836-5e73-49d7-9be3-8ad07caa6090	d11764719422d2c1daa05a58dc373ea5f8b6b874e0cd7317a89c27e50fe89ad9	e3999158111e4dcede408505ecbd0a8713fa2fa99045303873222459868881ff	2026-10-10 01:26:16.087098+05:30	2026-11-09 01:26:16.096932+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
5411b782-7214-4c5e-8f76-99eaac5e80bc	de526836-5e73-49d7-9be3-8ad07caa6090	d4b2a3b42c5f39cdb4077762ec9f5d3a9f175a7543ee7526dabeac312f66cfd7	9ecb154eed18e2de45c5f5fea71d5c0c50d419d88941f7de907627e8962a65bd	2026-10-10 01:33:43.923247+05:30	2026-11-09 01:33:43.932213+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
54b68e6c-42df-4f46-b4cd-ca2718ebf93c	de526836-5e73-49d7-9be3-8ad07caa6090	c2ae526d9dd4b6351970963e63519a18381733374f1d3e472a1370f775448483	e716ee021d50e6bdca3aa3fbd3feac53888b54d7cf7762983e4c02e0f64f2c28	2026-10-10 01:34:28.826902+05:30	2026-11-09 01:34:28.835349+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
387055bf-3e8e-4a0a-9460-db6eae815fb4	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	41c214d43f2da1ceaa963b46e9e97735300f35585685ac7727fa347fc0eef92f	456425ef5d9891e6bd97a61f6477849693f51b55129506ecf67a38084eec6d4a	2026-09-23 02:30:57.723752+05:30	2026-09-30 02:30:57.777855+05:30	\N	\N	103.171.172.132	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
48a21545-d72c-4a6b-89f7-e451e20a812c	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	94cc64dfd4ecc11e5f0b494f8abdce22f00a8ab4acfbd9ec7a5e987451018a01	e6f5698956585ba4066e31e198180d92bf4c7b03136a30c1cba3b1b2b0d12647	2026-09-23 16:24:27.252884+05:30	2026-09-30 16:24:27.346401+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
48d2f476-2c5a-4d5a-8453-c6d8e93fef24	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	bac423c795461e169813f1f9218fe843858b27e5fcfb508910479c98f82d9fbd	e6a568686e5f084f0f5eb3fdd8a6e62b8bc32977036f13cb2e61634278b508a7	2026-10-10 01:59:02.917482+05:30	2026-10-10 02:29:02.921424+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
0dbaac25-038e-4b52-a5f9-fd51751405e3	de526836-5e73-49d7-9be3-8ad07caa6090	e9400972151a6cf1fadcf4b20779cc2736cb6d14120cb4010645beb7154b8e75	62f03340cd621e1fb36306c21f6a75e566e55cce8916af430f5cc15713dc0d67	2026-10-10 02:00:12.668544+05:30	2026-11-09 02:00:12.681367+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
62303480-f901-494d-8e22-73215d2fdfdb	de526836-5e73-49d7-9be3-8ad07caa6090	1406bd741a3879fed05b9baa3bd60ddfa9330ffbcdda3c18c26221512348e1c1	b89de4a15ee17024a50e7e2d1be940ac6818326d641ff8adddd319d353af0d99	2026-09-21 00:13:50.441197+05:30	2026-09-28 00:13:50.506175+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
3a3d2cf1-bac4-4363-bae0-11d6c512fd22	de526836-5e73-49d7-9be3-8ad07caa6090	4c0a823d4048e4e57c6c90e2620dc987836d3141709557d079407e45681acd59	7042a55b1faf201fef47e9ba44c1d23e7553002ef95cad437f1d45488aeee886	2026-09-21 00:56:32.016102+05:30	2026-09-28 00:56:32.110402+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
f23ecb70-badf-4fb5-ad3d-4e6e60a4de94	de526836-5e73-49d7-9be3-8ad07caa6090	fa8fe2b40275bd2a0e3d58466f05d7d92622ca3ec444707bc9e7afd6f4001ae1	f10529bf3db6603ee695209c64229cc4efa6f7a8dcb65caf27079bfd1a3e7cd6	2026-09-21 02:16:53.265435+05:30	2026-09-28 02:16:53.345611+05:30	2026-09-21 02:16:56.676738+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
9388cd2f-a3a1-4eb5-911d-f9fef5e315c4	de526836-5e73-49d7-9be3-8ad07caa6090	a223295629f9b3a18a3c4940ca14b810f26369dce2fc1e36bbc66516252b1b56	587ca32eb95ecd1b6173583d1e858a4d5d8bc7d850e1ee61493508fb11d5a0de	2026-09-21 02:17:36.108162+05:30	2026-09-28 02:17:36.178441+05:30	2026-09-21 02:28:57.514511+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
2b359f72-272b-49bf-930a-8c2782d862b1	de526836-5e73-49d7-9be3-8ad07caa6090	8245ac3b1f51888cf069eb4e4b8d56372cb3671d977cbe6f04ab2f11befdb963	c28add07c21966da56147a87bd8a425e4612f5963619f30d05706ac8a43856ab	2026-09-29 22:33:51.692449+05:30	2026-10-29 22:33:51.760341+05:30	2026-10-06 23:16:24.750772+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
2559ab27-9091-44e4-aafa-217d42063f28	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	3b477cfe3995aef86631e399ce6ad634eaf3aff9a385a17f585d0aed5bd3363a	0c7cd2e440dabe58db87910190fe92bc690cdb46840b8aa55cb56993903fecce	2026-10-07 02:23:27.854467+05:30	2026-10-07 02:53:27.871498+05:30	2026-10-07 02:23:46.96456+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
d9561948-644f-4168-909c-fb067b066147	de526836-5e73-49d7-9be3-8ad07caa6090	fa27e32c57720b58522ffcc8a4996f432448810e4de88ee0577d48567b236452	553cc201939d5aa4a57621166d8886d9b7375b5c0e497211fc4468d5322ed87c	2026-10-07 02:23:46.962638+05:30	2026-11-06 02:23:46.973878+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
97171726-ea21-4fcd-9ba9-04598b83a19d	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	294036afbea6dcf5cf527c0c2d7050903ac6fd52e5e3919b8a042ffecfc03280	4cb1a5ec0bed82f01d2bc30059d3f5352925a5d90f85a8ebcc86be95033c1e6a	2026-09-21 23:40:33.439035+05:30	2026-09-28 23:40:33.511232+05:30	2026-09-21 23:42:02.798064+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
fd8e0897-79a3-454d-91ec-ad9007c61b8b	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	b3f7b66ed9b364652368fda88b218146ed471d0114ed3f6f1bf18d00b9b4ef7c	497477945db8ae4b36e4f1a5a8614766c9cfbdb21c4669f13b9455d07046e272	2026-09-21 23:42:17.944175+05:30	2026-09-28 23:42:18.038634+05:30	2026-09-21 23:42:34.537095+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
cc8cdc1e-e5b6-4cab-b2a0-cefee09f8cc1	0438f197-65cc-4fb2-8667-bdaceee1db81	dcb54c2366faeca53245ed0e4e50f91b2fd96896d258b9c4bba7f611ca7b7ec9	679247ffdbb90fe4d2d30c2c3051d9284a5913be62facb40959437ac6220db82	2026-10-07 02:24:23.138986+05:30	2026-10-07 02:54:23.141551+05:30	2026-10-07 02:24:33.446266+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
4da4882a-dc6b-4245-9120-13d73f201b64	de526836-5e73-49d7-9be3-8ad07caa6090	a593b6c803176335d777f2b4728c60700e487f6eb4ca741eb0bdd71baf6bc9f5	f2fc8ede773a3fd2a923d8b816e90c135a35553fdde6f8aed1677d9af21f4e68	2026-10-07 02:24:33.4417+05:30	2026-11-06 02:24:33.449657+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
27dd537d-9b15-4342-96d6-41b59a2134ed	69984504-68fe-470a-9240-4a37edf511b8	40f412138871af056478af575a399f64e10d80b50fdd112f13dd82ad52af7738	ddc28277a46f8f3c5da2eade97ab61fe3707a23a385f25bbc0ee2b3e2652f982	2026-10-07 02:24:44.833961+05:30	2026-10-07 02:54:44.837667+05:30	2026-10-07 02:24:47.827591+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
8684e4bf-6368-47d9-91df-0526b8d4d9eb	0438f197-65cc-4fb2-8667-bdaceee1db81	a46bc04516a15a93c0c68f0b5112a46c45861fc1254e44b70603d7661245186d	024f4b6118ce14e03d90c94bfe4431a35e49ba78ed0b4e4f5138a1652a148081	2026-09-22 11:29:03.713847+05:30	2026-09-29 11:29:03.782112+05:30	2026-09-22 11:29:12.702651+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
97c5b0e7-5891-4c22-a170-0061fc28cdc9	de526836-5e73-49d7-9be3-8ad07caa6090	550c3cb1cfc344a12938d4d72cb3516f6b3229c26f35998107dd7a2092935c98	53cf29379e8a99ef328ac9c96757d4d4714580104a8e9323526cea0eb740de61	2026-10-07 02:24:47.824479+05:30	2026-11-06 02:24:47.829933+05:30	2026-10-07 02:26:11.468768+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
1f561824-d34c-4e07-9d3a-921904aa365f	0438f197-65cc-4fb2-8667-bdaceee1db81	320d307b5f3954987ab6dcf1fedc8375dd98873c7321393f849c0947e790e8cf	2c0d0bba7383d2c66f83e5a18ef392ea9c3c852bcec784f99e5957430be852b7	2026-09-22 11:29:21.218813+05:30	2026-09-29 11:29:21.271764+05:30	2026-09-22 11:29:46.481707+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
f340cb84-d577-4a72-8f70-118d0c44f651	69984504-68fe-470a-9240-4a37edf511b8	2f6e72a7f57f0366b4487ad2e6b2d46063774a6827c7cb408c63c648e22b5ecd	4bdffc030e946a9d7b1f3d42d70520b89c9e7c76643d6e075ccd469f7b60787b	2026-10-09 19:14:05.186724+05:30	2026-11-08 19:14:05.26948+05:30	2026-10-09 19:15:17.973629+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
83973f1e-a412-4bce-b9fc-5d78e35f4f96	69984504-68fe-470a-9240-4a37edf511b8	5235cd64a541e6ab5677626003f66c2d5e7aa02b6c8877016ff5ee4540284af5	a084fc76cc1e868102db0b3b7ff34babefd41d1c6ced289c6d6c8796fcc04bd1	2026-10-09 19:15:30.54335+05:30	2026-11-08 19:15:30.606203+05:30	2026-10-09 19:32:24.890709+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
fc8f3461-3c51-4714-b0e3-5c7d95cfb8c0	de526836-5e73-49d7-9be3-8ad07caa6090	13ac76d43625720bccb2cd4558e2f7ddad3d915556b948de3da7e13077d1c01c	98f739ecfe53e280f610a8e8489f059f826b9138a3e46a73419abf32a9c4581c	2026-09-23 16:50:26.509305+05:30	2026-09-30 16:50:26.57165+05:30	2026-09-23 16:50:32.968858+05:30	\N	2401:4900:1cd6:6f51:6944:a425:a124:b930	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
5df44044-f123-4dc0-8836-f9630ecacf59	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	579d8d8c7e5aa80c1534da485636db071b4cfd77b78dcb6bc28cb1bc3559ab02	6e31795c59bf724380d67088ad5494f59db9d9cf508c41736a379dba26acdbff	2026-10-10 01:28:36.237981+05:30	2026-10-10 01:58:36.244571+05:30	2026-10-10 01:28:40.89817+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
85b55ac0-3b95-4cd2-86cf-ee0ceecfbdbc	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	ff2d7fa4e8bc890535b025e95ef89d1ff281c48c98479c122df4b68c7561f356	bc9edaa4deda77826e041f4dc699fda94b4cc432c615e5f1c34636d425e386cc	2026-10-10 01:34:13.627935+05:30	2026-10-10 02:04:13.633664+05:30	2026-10-10 01:34:28.830545+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
bf19126d-b560-4d45-862f-05847a7addf3	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	6295ee4eec85fd19de9b6e693ca65f59996c63b7e00ba5d826ac327ae1aba509	c6b1e1a916c2d4c0b37ff80c0c1c8bb42e92cb281ab3f17375873fd567919174	2026-09-24 01:40:08.501221+05:30	2026-10-01 01:40:08.558954+05:30	2026-09-24 01:40:38.445461+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
13bb94c7-19bc-4b6d-b9a9-2d83f308f96c	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	e4c2453523b4087d178fc99d5b1c5a3d5915adb70933c9280f76cadccbe1447a	ed82a9266f15546778f58b9ca376a9fbfc592007c11c43c464e47d4d4b5447d4	2026-09-24 01:40:50.892847+05:30	2026-10-01 01:40:50.967276+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
04d64306-052e-4395-b191-9e234582911d	0438f197-65cc-4fb2-8667-bdaceee1db81	f5b86e271f4a7cc6e170673a7e561bbda19619a205be4094f1d43f9c9b3e9af7	0800f3f849e33084728557f45981e669b25f6e4be3b70720d17ac0868a92d6ef	2026-09-30 10:48:53.289646+05:30	2026-10-30 10:48:53.358595+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
80ee37c5-71f7-43cd-bb2d-53af46ae2eda	de526836-5e73-49d7-9be3-8ad07caa6090	58b4259ecaf6f6bfc7a1a0944d8c8ad2cb7cde3f1e1198f4d4d39efcdf0ccd23	3daac63d9545f2c20929bb67670d00edc9c1bbbcfb92aca5995fb78376282641	2026-09-21 02:29:28.26898+05:30	2026-09-28 02:29:28.339546+05:30	2026-09-21 02:30:45.840255+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
ab6fa3f7-6611-4f30-a351-6ec0576ab783	de526836-5e73-49d7-9be3-8ad07caa6090	4f6462a673dc91ec1296d7db462776bf4f76a5f9e80bc9f19f31f5c561ad3792	58ede42683350fc5d86d7036a747d490ac89221591c05a02ea8869457afb2aa2	2026-09-29 23:39:09.501687+05:30	2026-10-29 23:39:09.5713+05:30	2026-09-29 23:39:18.817581+05:30	\N	103.171.172.136	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
5aa4e0d6-c710-4c9b-9ee7-089de288e94b	de526836-5e73-49d7-9be3-8ad07caa6090	38b9e8f5f68a90eaf4dc8e3148fdae4db2bb005ffe04e5e75b46e29f5da67d39	02c1a82d9854190064c3f192843af6ee197a4a2108d86da5fae731dbe8a603fa	2026-09-29 23:40:26.798075+05:30	2026-10-29 23:40:26.866157+05:30	\N	\N	103.171.172.136	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
52958663-c14a-418a-99a4-3c79134a91ba	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	7b21d45a840503fc5aa4251bbd15e230fdb346aeef484e6a07616d53a972f302	2b76d49e99ca1abf0ab21665b0e08de2faf792f24619bc930ce08e78168738f7	2026-09-22 01:45:28.138868+05:30	2026-09-29 01:45:28.206825+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
288e025e-5d39-4260-adee-aeb569c1a935	de526836-5e73-49d7-9be3-8ad07caa6090	e15308f191862d3ca03e6b87000fcb59dca546a1b530452f001eb8950bcd7321	c874f327925986d48fff138803305eac142be4ddf19f8beec8f6ca74a46487b1	2026-10-07 02:26:29.018185+05:30	2026-11-06 02:26:29.080977+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
f820f32b-2c28-44c5-97e0-7facc5c55c5c	de526836-5e73-49d7-9be3-8ad07caa6090	3b55436cf257607aa6e4ba41e4f51eff7edac3953879271de95fa148d3ffe064	33b586bcbd33707c2eb836c55e87128fc0d7a939b09d772944c7e0fff76e83f1	2026-09-22 03:29:35.633676+05:30	2026-09-29 03:29:35.693291+05:30	2026-09-22 03:29:39.714368+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
e02c7472-3ab1-4152-a0c3-4927cfd34a3f	de526836-5e73-49d7-9be3-8ad07caa6090	ade25ed373ff8a242dbe85f809d41787538163e64cc1a18b4acec91178cdad9a	7b15534b16f1818068f218618ad0dda2bc1bc13d5d79e5f5c9036fd6628ba05e	2026-09-21 01:49:39.748414+05:30	2026-09-28 01:49:39.818841+05:30	2026-09-21 01:51:11.03954+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
d11d4055-af9c-4f44-b5c3-cd9a3fd3d19b	69984504-68fe-470a-9240-4a37edf511b8	41ffc7cbb61efbac83a24fefe047d5152a72194792542f0123acf9fbda7587b3	b1ac55bf641f5b779560818905a4996afc1f2774cd856bad61ba4a769e6ddf00	2026-10-10 00:18:22.342663+05:30	2026-11-09 00:18:22.398597+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
b4edeb59-8caa-49b4-90fd-fb1a24a8fa31	de526836-5e73-49d7-9be3-8ad07caa6090	791e36b8a78f28a5c4ef43c938160e04a16bee1464a5c4c82103ae29e9e3f76b	656720738c6e05aca403443c27db58e8d69bf8cb7802756426dd7aed4797411e	2026-10-10 01:28:40.89447+05:30	2026-11-09 01:28:40.906003+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
858c345e-c914-45c8-8850-2d57b41a3230	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	7e216760792f03dc4fb0e7a45a53b8cf49fa7d2ea3a3134c92e20991cb3db991	112bdb5cce9788b531c04cf386b257036cb202bdda6358b01d6831343dce95f2	2026-09-22 03:29:58.008393+05:30	2026-09-29 03:29:58.085521+05:30	2026-09-22 03:30:01.502805+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
08f8c50e-9a6e-47da-99f6-e349121bbc24	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	930c6b491bae6d52544c20410938e3d62ec812f93d393604feb3393931ccd56d	fc095aabc429177420b360714d6f335ed114cc558910cd633cd4435af5c0e2fa	2026-10-10 01:28:55.086355+05:30	2026-10-10 01:58:55.09051+05:30	2026-10-10 01:29:31.057602+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
8cd8cab7-d137-4daa-95ba-0e2be388a623	de526836-5e73-49d7-9be3-8ad07caa6090	fa979722e77802a349533efe8ab631afe5ea27c0325ee9d9557a2298ca73dea9	450c682647120b6ecb676b5e77d396efb14f1fb8e29bbcf1cd30e937f5d8a209	2026-10-10 01:35:51.563496+05:30	2026-11-09 01:35:51.580779+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
c5d6ee13-ca54-44cc-80fb-d1125a4a8dc4	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	6da7837b8d584e42c7602ec0ca1af633e6ea00f60dd9f7226e4a4b45902c5d0e	b2f52f79142666921824e08577be32709ed9cb9935104731b53376a053c92d8f	2026-10-10 01:51:31.757374+05:30	2026-10-10 02:21:31.760233+05:30	2026-10-10 01:53:33.753772+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
8fc714a6-1e27-4d41-91f4-a5a35de6a69e	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	2efe4e298f9165476256760847f2d8758f59d8600d2161608d6356a40f67383c	77a291c69ccd96abca62a49a9ca3adadd046a5d7c4284026f673f4127de7205b	2026-10-10 01:59:13.301111+05:30	2026-10-10 02:29:13.310914+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
0344f990-b03c-4764-a3b1-0c078375c33b	0438f197-65cc-4fb2-8667-bdaceee1db81	9c04140b016f1579701e60f43ecab1f9667e990424744c70b3e3df3b68eff294	3840ae192a519c84803f9939ff94995c638739598c4487cd5b73d7d25d2dd915	2026-09-22 11:30:37.549516+05:30	2026-09-29 11:30:37.622549+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
0fd8060b-df3b-45af-ada8-c97bc56e595b	0438f197-65cc-4fb2-8667-bdaceee1db81	11efd8f9e1a87f8d8af74239381e6638f9d9495c7ed5defc0555d6958a7ef5bf	2bbd2e44342759e076f15b7ba4558d086519decd0417b8355ced9c48e37359f4	2026-10-10 01:59:29.984566+05:30	2026-10-10 02:29:29.998536+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
e6fdcb7e-4a06-44b8-a9ba-254268210a54	0438f197-65cc-4fb2-8667-bdaceee1db81	ab8a8614fd665782461d1bf0088f33956ff154fc13c40db9a0dcb2092f3dcf5a	69694ea8d5ba6865b24ff3cf73bef77c9caad7204b789dc8aaa4fc8a005bdfc9	2026-09-24 00:06:07.231751+05:30	2026-10-01 00:06:07.303404+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
749042ae-c710-44d2-bd82-9907dbf373bb	0438f197-65cc-4fb2-8667-bdaceee1db81	0e41f4133a0fc395591f390ca4fbf7a1440f2b7e3e22ea812a07aa38fb30dfd3	6e492ae02469e4d38691e2e9b245a6c36ec4803057a90f3234747d9376d12b46	2026-09-24 01:36:57.795389+05:30	2026-10-01 01:36:57.861664+05:30	2026-09-24 01:40:03.007452+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
d82c585d-7573-4597-881d-33a1b3e3f86f	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	dc964425a1bad87c05864d40f0993799ddfec357fd40f911ce1572cf86316d4d	7e3e8d7e73a4d64402349f17c7d2b0b1663acc70db37bf41f618ead7b6dc69c0	2026-09-24 02:11:27.799475+05:30	2026-10-01 02:11:27.871087+05:30	2026-09-24 02:25:57.704979+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
6dff99bb-b1e2-428d-b88c-4614202e6be7	de526836-5e73-49d7-9be3-8ad07caa6090	a8c99d45cb58db7ef95dc355ec16b9e9dd9d88a96f7e4025e953a9a3a18b1d34	b519b51fa7286218c13deb997d38aad1214a8c9884167d81ab13adacf905a084	2026-09-21 11:29:38.802595+05:30	2026-09-28 11:29:38.889377+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
3525e3e6-23c5-4c64-8d84-3b816edea0a1	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	1d7a95c8c41edea02ced6c2610137b0ba7a9c45a029cae17c8f80cb77ea92158	9765f3389d8bf65ceb2003a771e4ab300e9a9b46093f3b4eab8588ff6fbe445d	2026-09-24 02:45:35.618468+05:30	2026-10-01 02:45:35.683147+05:30	2026-09-24 02:46:33.370736+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
8ea3262b-3cbe-4b3e-9297-53c34887c49d	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	bca9efe8d5ccff6110c3ceee04855e78e72a10c48d284734d07aa41be922f7e4	d2f0874b1ef87eb121ce3d78cfb32deed642d675598f0c10f91016f5369cee79	2026-09-24 02:46:52.543767+05:30	2026-10-01 02:46:52.609953+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
b1e3cdd0-600f-4cc1-b990-cc3f2224dad7	0438f197-65cc-4fb2-8667-bdaceee1db81	adef4f0bf0face77f0e829c6434a1ae960d3fb6ed6f19798f42c1f49865cae2c	5459d9041fb4b43389e9c15b57f541aaa2447071b7fd52debcbe90a959c37655	2026-10-08 23:58:52.898449+05:30	2026-11-07 23:58:52.967631+05:30	2026-10-09 00:37:12.962659+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
ceeb2e35-7b6b-48dc-9410-fed728b26409	69984504-68fe-470a-9240-4a37edf511b8	5ba869d8fd6624e630056be5e15bea661724fbdace562cbf90fb0831f3b92fba	b1680c1ecf63c9ad70c68486ffa9f0fb3c74708a4d27d3fceac90bf966d9f1b4	2026-10-10 01:24:28.941023+05:30	2026-10-10 01:54:28.951541+05:30	\N	\N	\N	\N
20928bec-8ab0-4221-8378-4255a2ad5228	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	0b7efda6ec2906169803c8720008788edb1b3d293fe43d1ea967f1ee27ea5e9e	9d7917ecff98673b8a83b9a2de44a4934077cc2656172490d9459a15e38e2a6a	2026-09-24 03:23:38.952635+05:30	2026-10-01 03:23:39.027197+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
f08b613f-3a39-4e1b-92b9-5f29a86fd976	de526836-5e73-49d7-9be3-8ad07caa6090	dc36c37803710ffbc2c3ba3d095022c1c73c7c82aaad20dc4459cc539cd35b7f	c4e51f2437d44fbf78ea4972506731c26c2d463176506e069994b6178d8d623a	2026-10-10 01:29:31.054082+05:30	2026-11-09 01:29:31.063868+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
2ba2a7d2-46b4-404b-9e45-89f790e7d292	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	e4345e19dee2e72fccecc970748fbf579631ac7c8d4a10fc7935547eb0a75594	b34ff3d6f4762d78c4b85a94432868cc37cc18413a9ef6f54377844dae7ec0be	2026-09-25 11:08:59.713514+05:30	2026-10-02 11:08:59.777589+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
7f2f465f-859b-46ce-9d6f-0aab4498f6f3	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	6dc00734f656587b6a676ad358a7fe397b82c6d3007ea154300fc80bb508a741	535efca1af266924f47cd226010c1b9de59e8b74183cec86e212638270781d5f	2026-10-10 01:50:04.072966+05:30	2026-10-10 02:20:04.079515+05:30	2026-10-10 01:50:17.169461+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
d26477ae-7252-4e44-9be1-2138ac7e4f4e	de526836-5e73-49d7-9be3-8ad07caa6090	2d35f0a02e47706618162ecafc44f3a844a261cc4179e2c4e755572a8adba361	d3bfc45125be9188d7321c67d0213252a331ceb6aa057ca5a3c242c1a8c254c2	2026-09-25 11:32:21.824903+05:30	2026-10-02 11:32:21.918685+05:30	2026-09-25 11:32:24.434448+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
1df097e6-7b9e-4cc7-a28b-b4d800b6fb2e	de526836-5e73-49d7-9be3-8ad07caa6090	d3019edc8045b12fb1ecfff6039fbdf92010be53649ffcf9b4e0f9fb18d6e3a2	03c172ce8884c3ae836b64509b6abfbbd87547ab282e82af3e08647b7d3592dc	2026-10-10 01:50:17.167146+05:30	2026-11-09 01:50:17.172674+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
415de81e-75c8-4f64-9979-c40c84e8c710	de526836-5e73-49d7-9be3-8ad07caa6090	41f80e0e20dab0cf93b9bf56da0cf5746dbce69c4da2ef4503380433a34594bd	aca1b6a5e9d91e9f2d04febb001bfd59985e7e69f68f90c696717c52f0ac8167	2026-09-25 11:32:35.004831+05:30	2026-10-02 11:32:35.074714+05:30	2026-09-25 11:32:36.729039+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
86aa0bd4-dcc7-4540-98d0-a0f264ddbc46	de526836-5e73-49d7-9be3-8ad07caa6090	90824a627483024dc37a8a4209b829ccbf3620daa51351fa59908e4479bfb548	a65bf00211f3ebc08277e5011b871150f130e7985487e4ac1fe69bc45be63f65	2026-10-10 01:50:39.581532+05:30	2026-11-09 01:50:39.586545+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
fdad8a23-6b09-4990-a4f3-c863f937adaf	0438f197-65cc-4fb2-8667-bdaceee1db81	105685e1bf89ee1c6928b1d99947bc4640ef1c098e0554370f04515d6421f795	3592845967d132ab86a52c4df0fba35ee994924c090f61df6783df5850156574	2026-09-24 02:26:20.737377+05:30	2026-10-01 02:26:20.805907+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
594dc801-7834-4ac1-81e9-8fdaad1965e1	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	55fdd4a58b0ab4fcad59a67085b4cbfb2142e67e67ad1ed96a04813be3324d64	32414a68997c9e14928e8932e80731be33a4c677258d38e3b3c2d758962d71d3	2026-09-25 14:03:47.466+05:30	2026-10-02 14:03:47.536115+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
4953fb7f-b4ef-4483-b263-aa7f583cee77	0438f197-65cc-4fb2-8667-bdaceee1db81	d96f6a3c6c87c67fe710fe585e0321023245c49a13b2c3f0f3c74f9475b417a5	7e6fb79d7debccd443f68b84270825013fa3bb6216930a6eda819003f2ba7949	2026-09-24 02:45:16.780273+05:30	2026-10-01 02:45:16.840016+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
16cb298f-d0df-4902-920a-2cfaf36822b5	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	f26adb8082587d8a3d9bbce1f8b04b4e24f0318d63769970021935c1ca80cfea	02b555d2975480d6549069c262925dc95616223f95f0fe5cef712955a8b4927f	2026-09-25 18:49:54.968727+05:30	2026-10-02 18:49:55.03561+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
9bd63703-2efe-4309-8fd3-6df6a1056d44	de526836-5e73-49d7-9be3-8ad07caa6090	59bb2d5cb1bc3cbfc1ea870d31d49fb47eb761b7b5244d02976af7ccd2587a14	35836de69decef1d1807967c1bfc051d9c1f64ab7a9e5fcd4becc683aa1cff3a	2026-09-25 23:11:53.323556+05:30	2026-10-02 23:11:53.382524+05:30	2026-09-25 23:11:56.192215+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
c110fa6a-f5d0-4e35-b4fa-daa6158208a7	0438f197-65cc-4fb2-8667-bdaceee1db81	5fb4da0d51b111d04fc3b74c7c6655455b5c1093a000de5e23ac191039d318a2	84f80f539dccefd814d7398aa954208e93415e5cc69f6c6a2eee435bf56ddaea	2026-09-25 23:22:27.756683+05:30	2026-10-02 23:22:27.83462+05:30	2026-09-25 23:22:32.742501+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
1fa52794-9c28-4e12-9017-0ca9c0ac75f8	de526836-5e73-49d7-9be3-8ad07caa6090	ab62c1dd8091a2667f14df4ad13f0d2655f19fe38b6da5688225a18f784db3c8	8dd9026c89268d1ab77132c1a88118f160fc16ffc2080d754a6f4a3fb2fbc581	2026-09-24 02:47:31.322844+05:30	2026-10-01 02:47:31.398182+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
2d3d1a6a-2c11-4d7f-a948-d33861be2e64	de526836-5e73-49d7-9be3-8ad07caa6090	cf6cc4c7f3683e3d14374bdf2c50fb595d2116bb7579a397717942936feabec5	fc9ef783d94e191416e7015b254ee27b32ee32bcc4989c0ff5af5bff92737cc6	2026-09-24 03:22:57.641257+05:30	2026-10-01 03:22:57.69567+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
fbf3fbe1-d20c-4153-bbba-a58f021205ed	de526836-5e73-49d7-9be3-8ad07caa6090	f29abca5b47bf6051f43165838c05c3a8c3bbd3a6875e8eed03096ede1412447	cb2eeb44b70b892ecf810db43a5fea5961d27f7c02a82b0dd257b0c4c81bcc46	2026-09-24 23:18:32.861186+05:30	2026-10-01 23:18:32.924178+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
2b635ee4-0c69-4838-9533-0e155a888633	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	c99511ffa2cc6ceaab1f25b2dc77fc1355a7f62b81b68eb058d78af52d7186c7	5d44b5d332235764cbda6c579cc28d9a0b197cd2e78fbba43cc953dc22a4cd91	2026-09-25 23:13:01.919949+05:30	2026-10-02 23:13:01.995703+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
131f2787-0392-4025-b5b1-8ecea3a4b650	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	836a24592d2de997017daa6e8ddb570959bd57bf171941c32b28116b6ca61e25	e19d4b970a739bb6d0cb52bf1dc3dae19418bbe74ff03e9ddf9a1a5ecce5444d	2026-10-09 00:37:29.932508+05:30	2026-11-08 00:37:29.997737+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
4be679a3-38af-4d2a-868e-cb4dd9cc16f1	0438f197-65cc-4fb2-8667-bdaceee1db81	94e359725b73f366cde8e0a3490fd510074f7aec764ef1504ea673a95b54291a	d4714608f654cc3d06f5082ee71cea8a50725ff344ba95af0784d2e2411da021	2026-09-25 23:13:52.518591+05:30	2026-10-02 23:13:52.581532+05:30	2026-09-25 23:22:26.027073+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
3698e2a3-8b96-40df-8300-3fe9140b2b79	0438f197-65cc-4fb2-8667-bdaceee1db81	c5bbef4f7a5eefadae9626695f873a07b0ed39099aed91b741c6d55782bebcf8	e11b22110d37e38894091c9a1635d670553bcc787ec5f5bfc55c955905871ea4	2026-09-25 23:22:34.686301+05:30	2026-10-02 23:22:34.758518+05:30	2026-09-25 23:22:36.256861+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
fca428be-1c5d-4217-9f98-1de9c5eb5140	69984504-68fe-470a-9240-4a37edf511b8	3ecc277b7f58059dc42443ee137dd7ea0fc5d58b37e630c74f37aeb37daaa650	66c726e847af3f514229af041696a8d96eaa7e2c5391bf2e41415c2ca84444d0	2026-10-10 01:25:07.221223+05:30	2026-10-10 01:55:07.22568+05:30	2026-10-10 01:25:40.59729+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
69966b43-1cf2-4997-aa6a-819311e012f3	0438f197-65cc-4fb2-8667-bdaceee1db81	2dc7c6c221627408a3f94a9276fc7d86202e88a427a8e46fbb336b011c00f42a	84d1daccb2f4af31b567c1b17bb903bd0a6a140b800fb59a2b046b91d687f83a	2026-09-25 23:23:02.070163+05:30	2026-10-02 23:23:02.142513+05:30	2026-09-25 23:23:05.518361+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
654a314a-9003-420c-887d-60b8ca24e441	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	8c400d248dd2c6984a205b7cbe47d15e7e400364877ff0073da1da87a4357cc7	46e254b47bbcd9fb1f147d7a38fd6e5a6a17e02a41a7d00a56a399af7658b4e4	2026-09-25 23:39:28.940519+05:30	2026-10-02 23:39:29.020071+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
46874b8d-7039-4ca3-b520-5d51e03e7a73	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	bedbe517b1269043c76cb7eaa61aac06fdaa1409e11aac172e8cd71036d549c2	4679bc9f37df597c12ab62590fd7db16cb52fd685f08510490c86cd34b54680a	2026-09-26 00:12:13.328075+05:30	2026-10-03 00:12:13.389118+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
aca26ea2-916e-49ca-966a-42493ff6be9d	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0b92efac180794413d6ce9d2a0ad486d844a92bc5104e70ac3ce38be9ab8bf32	aa3919e6ab30671f416cd73aec68ae32189a84424f19ca7cae23a311e487710c	2026-10-10 01:29:37.469881+05:30	2026-10-10 01:59:37.474017+05:30	2026-10-10 01:29:56.372696+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
c5ca76c8-1248-4e7e-8853-f8dd0bbf6d31	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	72e6ce28a102bfcd5244b8db2609dee24416d5ad1f9e067a93ff56f8064b7acf	143953a1d91193e9ea1aeada6e163a608386b8813ccafd42cd135c61e4494d4a	2026-09-26 01:16:41.8526+05:30	2026-10-03 01:16:41.917423+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
4a755745-0504-43e0-9fec-62fc42bc59b9	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0cc2191e69e8f515009a2a3614bd9deb0fb097287b087fad46997950512ba6ae	54752612f899d50447f17a0fdf763bffb74f294316fea7badc0c23a91264cc98	2026-10-10 01:50:26.472372+05:30	2026-10-10 02:20:26.475891+05:30	2026-10-10 01:50:39.584321+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
797d76dd-b806-4d43-a88e-05acb911e225	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	9cb0589dcb6e09b48be9cecd86e7bc58a4bbb8e9d7f3c7480e9ba9cf217562bc	e768a9adab75fe7b01005dbe994b5a3e646ff877952d81460290af17ea563eb6	2026-10-10 01:51:22.955517+05:30	2026-10-10 02:21:22.961489+05:30	2026-10-10 01:51:28.682019+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
0e43b6db-559a-41b4-af41-4550af84431c	de526836-5e73-49d7-9be3-8ad07caa6090	adec78363ffc74212865effb2a91a26dba0f7ca4157576a6826371ac116dca74	c91e8853b8faea877782c313e6442aef4b4805ce3799cd5b23d5b8f2d991c77d	2026-10-10 01:53:33.747489+05:30	2026-11-09 01:53:33.761982+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
1d7f71fc-2afc-474c-9a90-8b9189193a0d	de526836-5e73-49d7-9be3-8ad07caa6090	7e70b7f003ad34f42cda1b9210faffe365266af0debd0194f0bb9062bc387770	3a70965fe9123dad72c68329476ab16569775354857c91a34ceddbf6841b7fdc	2026-09-28 15:53:34.945127+05:30	2026-10-05 15:53:35.010787+05:30	2026-09-28 16:01:39.394892+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
46bf104e-7d91-42a3-9463-545293db4014	0438f197-65cc-4fb2-8667-bdaceee1db81	e6e3a177087da9f4e08667bae560c03c76c10f33f586f630850366a4f44a698d	270c57520d1a29872526ac966e38dfc9ccae0ab67297313961a177c191235e37	2026-09-25 23:23:19.139521+05:30	2026-10-02 23:23:19.214994+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
5ce33e17-d168-4c9d-8241-db28ca8d7cfb	de526836-5e73-49d7-9be3-8ad07caa6090	983d3997eff36959b52e1e78b09ada1e66734472204398fc588c095581b3fc24	7cf103b50a2155bc37c6cc1b578338417cbc072dcb312a71a6b2f7bea76c9d35	2026-09-26 00:09:14.67182+05:30	2026-10-03 00:09:14.727542+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
a8f713f5-dd4e-482e-a7ce-b1c0e4c3c1f0	69984504-68fe-470a-9240-4a37edf511b8	f1f297385169d12dd2d9d0ff124c92e16c3a4fb6779cfc2ca567dcb643db268d	4e1cd4019c300f9a3e4e656debd4b70c8e331f7853b3916db1a3dca2e486a431	2026-10-10 01:25:37.116699+05:30	2026-10-10 01:55:37.130962+05:30	\N	\N	\N	\N
054d1a1d-e01d-4cb3-8ca7-332d5315c8f5	69984504-68fe-470a-9240-4a37edf511b8	7a98241d7438dedbbd1235aba19bbfec403d54f417d165b1cdc90a3e81bac790	2ea335e5a5b7f717dd97be844cdf55ccea880246e061d25ef906d95c7d2cb03d	2026-10-10 01:25:37.162669+05:30	2026-10-10 01:55:37.164056+05:30	\N	\N	\N	\N
5ee3329d-c96a-4efa-b061-4cca57bd38a6	69984504-68fe-470a-9240-4a37edf511b8	21eefc049ecaaccd320ea5a515614cf9e2b9abc11c56e2489c1457bbe46be3bc	4b8006b120e4a0f6eca1f565ab11625e8ffaf3ebb1ea862d1cb79dd36ad287a8	2026-10-10 01:25:37.167438+05:30	2026-10-10 01:55:37.16938+05:30	\N	\N	\N	\N
ff77491d-713b-430f-8972-83b4695f0598	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	d7b67d1f77156611394bc51336854c98f9ec05c42cc83dbff2394559504e4264	57b389a6f1182cb8c2b1eb39b0744eb0dde512675ac1287f6ea36ee176494abb	2026-10-10 01:25:37.173812+05:30	2026-10-10 01:55:37.178916+05:30	\N	\N	\N	\N
733e9807-72ef-42c1-929a-de49f49d75ac	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	89c5d2a01ab404dd27e1681df83930c589af2501fc4b1e477faf936bad263814	bc21b2ae6f19d1c4727aba1d66341f64ac34cf06cc9d182739382652d85ac577	2026-10-10 01:25:37.181975+05:30	2026-10-10 01:55:37.183137+05:30	\N	\N	\N	\N
dd9e5d0b-1cac-41d3-8550-9825838a41e1	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	fd2ac9d351289d7332b45f6867d78071a351b1925d4470ae7d6d462029bb1355	c3a02805b0cfccd4fa6712d2b1a8a53d7f9f64b35d0e944fedceffb34b06c26d	2026-10-10 01:25:37.186791+05:30	2026-10-10 01:55:37.188222+05:30	\N	\N	\N	\N
cb4d6113-b99a-418b-bf99-ccea77751a6a	69984504-68fe-470a-9240-4a37edf511b8	52361eff8c39e5c1a8abed8472fc3cf97448de0b36e2d1f131f59f67434456d1	2e754273fe7ac83c50dd76a4e0180d0a63c550617cb1feea08bd3d0afb5a9af0	2026-10-10 01:25:37.191601+05:30	2026-10-10 01:55:37.194918+05:30	\N	\N	\N	\N
e7a11336-47f6-4fe8-b092-bb95ac24d6c8	de526836-5e73-49d7-9be3-8ad07caa6090	1755f77c909d8c007d4d33564c548f47731ff96b5d61938c1a28860cb8ebf83f	a0e2a84169d5f749fd07baba23149106fa28bf8e70e7dddd8107caf6cb8255a5	2026-10-10 01:29:56.361877+05:30	2026-11-09 01:29:56.440477+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
23dc66bc-fcd2-4537-9518-12587385d15e	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	c87ca320df81629d99898127e5c1871da52d5862d87819bdc9d37ed550be0f16	a5f9763b0b6d0f03d101e68ae2d5102672dac1a0e9877162b409a87f1c3bfee9	2026-10-10 01:50:54.259079+05:30	2026-10-10 02:20:54.264573+05:30	2026-10-10 01:51:19.34247+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
b37d5696-27dc-4436-825e-6c09042fb323	de526836-5e73-49d7-9be3-8ad07caa6090	500e95211691d7c95782349ead362ab71d68474d7e7cda4ca66b97817f9c7398	c866ae583a44fc4d3399bbe356462950362a83f954b9ab0deb1639c38ee69137	2026-10-10 01:51:19.337134+05:30	2026-11-09 01:51:19.349175+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
e101de10-21c7-4a05-9df8-6ef5515fccdb	de526836-5e73-49d7-9be3-8ad07caa6090	5dd5af32b57001b4b6d53be6de19bb30597b789ae804b7343e75cd8c20e62ad7	f01c6b32d6f2765dc3fae9c9c40df1f6647a48c0b4ab1e976a9bc8e6997d29e2	2026-09-29 10:49:43.111774+05:30	2026-10-29 10:49:43.177703+05:30	2026-09-29 13:54:48.486811+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
1da93fa2-50f6-4bc8-8a05-a8a20ae701d7	4ce61bc1-113e-42e4-a934-c58c9d61e541	f09513a3bc9a7f2d50ff358566fe714dd3aac977eae8c9eeef93130249152883	93dd42fae80aaad59cdb79bac28e49185dd93ce7ec661b7ff9128cd864abe456	2026-10-10 01:59:47.781882+05:30	2026-10-10 02:29:47.813965+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
1ed3a5f8-dd93-4de4-a107-9c6714f1db09	de526836-5e73-49d7-9be3-8ad07caa6090	69f8a5ba2895bbe30f4ffa6161a6e9b8363cbf38fea99925da154c6c4f68d473	18657532702c13b1b2cc130040fd0e72a9fc417fb452a4273bbd66d895d311d0	2026-09-29 13:54:55.848003+05:30	2026-10-29 13:54:55.922139+05:30	2026-09-29 13:54:57.405031+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
131863af-f9d7-4070-a3e7-646cc431cecc	de526836-5e73-49d7-9be3-8ad07caa6090	5a0280f9fd30f84b0c65c4854d8b5158d72dadec4eef06d8835b1f7e68562578	aecc4a6af1f97886202a9760034a54417054bbe70434be403b14774534eb317a	2026-09-29 13:55:06.631635+05:30	2026-10-29 13:55:06.702811+05:30	2026-09-29 13:55:09.358503+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
f2019d0a-df75-4046-b714-5b74030b5adc	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	3257882a64906454d2243814d47732edd9e6c32658169673dede32ccd1da1d42	f2cd7c8fdc18b7d9fd11e81386cdf28b41ae6146ae22fd69f257b1ebffc61cb3	2026-10-10 02:39:40.468562+05:30	2026-10-10 03:09:40.47715+05:30	2026-10-10 02:39:59.745704+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
e2448b13-c6f9-426c-a90f-5dff69b98c12	de526836-5e73-49d7-9be3-8ad07caa6090	ed5b16ba0765abea1a40a00e2c4a4a7fe8dfce7bbc58e08ad2497552396e4b9d	0a5de2bdd53ed9c350a9b971583d679b2a6f71f991b1a9ae8beaa28dd7852660	2026-09-29 13:55:19.014685+05:30	2026-10-29 13:55:19.08463+05:30	2026-09-29 13:55:21.441862+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
afd1aa01-f6e0-4064-af87-ebaf5886d9a7	0438f197-65cc-4fb2-8667-bdaceee1db81	487ebc3c329ea6972edad125fecc48cdf1a479dfffd75230c59f82ac6d2220ef	c5c2211c9160b1104d46242278b4c74c3b5062d5e8ba47b62713bb356904649c	2026-09-29 01:16:33.235503+05:30	2026-10-06 01:16:33.307142+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
1cef34eb-1636-4e45-b85a-8760228ec2e6	de526836-5e73-49d7-9be3-8ad07caa6090	f18cdc73df5c706ce68a5acacbd476d5dffc140e15bc75bbee0b78f85ceeea1f	5cab316658f33b484139106e580d96b5e6b2c0c48d2aebf1815240c6b5cc4873	2026-09-21 01:17:40.607961+05:30	2026-09-28 01:17:40.698185+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
10313763-7c74-41d4-a129-761c6f0102df	de526836-5e73-49d7-9be3-8ad07caa6090	8980d4c970b54c3079f61b8227ec2b615fd0e09237dcf319b470e9b1d36b895d	f096cf12c87ff725dd7223eed32e89e66502d811e8caa4e2cb0430f6a22c3ec7	2026-09-21 02:38:09.873974+05:30	2026-09-28 02:38:09.959732+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
4a798242-fad8-436d-8195-c8f6e4898995	de526836-5e73-49d7-9be3-8ad07caa6090	cfc1bdc0c8e0915ab1eb96a23a034adbe9770c0fdefc181df10c34b6c3f380fb	ed5205beee6b99e599f1cc51ced877ebbec7f18cf9ca394278705043b7353508	2026-09-22 03:32:11.129796+05:30	2026-09-29 03:32:11.202993+05:30	2026-09-29 14:26:28.612116+05:30	\N	103.171.172.150	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
f2905b79-8b29-4f39-83aa-2c125a0f371e	de526836-5e73-49d7-9be3-8ad07caa6090	73067a81177764fdcb9fcc38b9c461c116e743c4ad72c170b9de1676bf8153fa	bf2697cb536fedf553cd21a3a7ac9290173a610bb4385025e09ae0762e270d34	2026-09-28 22:52:38.760062+05:30	2026-10-05 22:52:38.822946+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
6dc2b052-e4bc-4207-81ca-42c7be48822b	de526836-5e73-49d7-9be3-8ad07caa6090	7e7f8aa90eb5286b01517b201ebe243a3324365d66e27d92437ab085a70411ac	fb9775ef1097ab80171c6758e0162ca456af80d00c7b7f97da210af2068ef71d	2026-09-28 23:13:29.702784+05:30	2026-10-05 23:13:29.789636+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
d9654ef6-0a02-425b-8c0a-7670045b3a4c	de526836-5e73-49d7-9be3-8ad07caa6090	164432b2a8d6c62d5505af7995863531fb946f0c96d60c912e6901aa71da2b8e	18a2f1dcfb701ce3aebe7c46c1704555a6eca1227187fabbe78a97a7cec4a645	2026-09-28 23:35:42.741534+05:30	2026-10-05 23:35:42.814823+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
b1594d3f-2865-49bd-acf7-8126eaabd4f6	de526836-5e73-49d7-9be3-8ad07caa6090	60a1e318fbbf4751ecfc519b5dc145cf66b3d8b10f9d088e6156f8b6b7532adb	cb8e644b22d70741d3a6d55efb7408e7d941a505cb363886bb3be843ab4510f2	2026-09-28 23:37:23.099157+05:30	2026-10-05 23:37:23.186013+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
8c4e243c-0e3e-4eb1-a8c3-e9dc9c472d37	de526836-5e73-49d7-9be3-8ad07caa6090	dbd4be653565a27a320b501c9ca15554f649032513b75ce9e6284b02df1edf88	ffe6efabc51df85019c25265a328c5bd698013d41112046f5fdc92e5e2620ca7	2026-09-22 23:36:05.550501+05:30	2026-09-29 23:36:05.606172+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
9bb4edb1-74ce-440c-85aa-9a2c896c4e2a	de526836-5e73-49d7-9be3-8ad07caa6090	a760d2182227f6e27684d65ce2fa0831d5ce79ec9ed1fa80a095051af35960e0	010d43a47e427d0485530cb8135bb6c7afed05ff1f514a6ffe91b85bcc5a4436	2026-09-23 01:45:14.089923+05:30	2026-09-30 01:45:14.136666+05:30	2026-09-29 14:26:28.612116+05:30	\N	103.171.172.132	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
c60d043d-6689-4c2d-857a-48cc8dd1bbb7	de526836-5e73-49d7-9be3-8ad07caa6090	97983b1843995d588ff1f948fb92e6a800b2ffb68cd9e1a63399c15913c5b346	eecf3d2d09d752ca441e37c13a98a6e46096ac82b75d0169e918b585193533fc	2026-09-23 02:25:11.811324+05:30	2026-09-30 02:25:11.89413+05:30	2026-09-29 14:26:28.612116+05:30	\N	103.171.172.132	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
cd948024-4b27-4207-a13d-20f090b48cd4	de526836-5e73-49d7-9be3-8ad07caa6090	b69269cd170283ffcc1870eea8e5d4a0b96e6d82af5e2eaeb8f20e2b591cfee9	e10bd9b99a8dbc4e0ffc324dc25f96e9024895cbbeff15ffbfd422eb281e60ff	2026-09-23 16:56:26.187047+05:30	2026-09-30 16:56:26.243578+05:30	2026-09-29 14:26:28.612116+05:30	\N	2401:4900:1cd6:6f51:6944:a425:a124:b930	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
75bafcdf-ad23-432e-912f-996f4d54ba80	de526836-5e73-49d7-9be3-8ad07caa6090	e71733329c567e1c41413eef80350e090b83d09cf6a002af86608c41d58e115f	daacf4a2e7116cca59c7d2ba60210f33bf42b0a62f85ac7fd8dcf15d0aecb710	2026-09-23 17:30:37.952877+05:30	2026-09-30 17:30:38.035159+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
d16dc0de-f130-45eb-b5f8-a98271b8e8a9	de526836-5e73-49d7-9be3-8ad07caa6090	d1b25811433aeb8c5d78b51c937f3a56d863fa380c7f43ac837b9c1e86b96654	e529d8f03fde18b96ccbde475e8bebf9d45e7a54ffe26d837097913c9291527c	2026-09-23 17:32:41.274287+05:30	2026-09-30 17:32:41.345585+05:30	2026-09-29 14:26:28.612116+05:30	\N	2401:4900:8811:109b:e015:265:f23d:eab1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
15fd5a61-9d51-4324-9361-7a3ba435e58f	de526836-5e73-49d7-9be3-8ad07caa6090	c3c77b72babe1024fc8c8dd8a93f38a5fdabdc193f4a1cd09bdc484bf55e1846	52c350c25cb36263cfd0708f9a127258b0eea5bd23a3602a4f18e1bb94dbbce8	2026-09-23 23:03:07.067794+05:30	2026-09-30 23:03:07.157452+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
d5fbc6e4-4f4a-44ea-90d9-2b31a64d4506	de526836-5e73-49d7-9be3-8ad07caa6090	e6084e683adbeb913bafdb0fa10abf053487c2e2a44a2caaff7abd299f20d2dd	efb6580582f5f957da502811d9c6d0e97f6dc76ad3a81189e82fbc29960c41cc	2026-09-21 10:56:43.089579+05:30	2026-09-28 10:56:43.155862+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
cadef5f4-de47-404e-8ab0-6ea2960d4965	de526836-5e73-49d7-9be3-8ad07caa6090	9d62e13b1d19dd17b81b72d875ad189db8b89cf4f7898f556106ff4a8584de19	d288687e4cc8886cbddda8df438722b881a2b0ced0ee471d7b2741fdb3244a2a	2026-09-21 16:08:53.439993+05:30	2026-09-28 16:08:53.520086+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
475b6cdf-86b4-4b05-93ca-b6e5c3961da8	de526836-5e73-49d7-9be3-8ad07caa6090	5d4389b23044c4ca757e08f27887172a45657f2bdc39264f23a7939a4c8168b0	d42a9533e615a9f5b9b6cb31f92dd799ea85ef10ea4e8b0a59e555f81db1f059	2026-09-21 23:25:19.907755+05:30	2026-09-28 23:25:19.980118+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
49936ad5-c6c1-458a-ab38-61b2a876dc8e	de526836-5e73-49d7-9be3-8ad07caa6090	9c11d85b801776e781c56390a0945795f44227e6dc8a0e66cf5e8b7007a907ae	06c67b7f5d02104d2ceb582398e411f4f04ee9d526bfffe55bb879ca03fb6e67	2026-09-22 00:54:13.295407+05:30	2026-09-29 00:54:13.371977+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
57afc162-68ff-4b8d-b33f-72588ba34bf6	de526836-5e73-49d7-9be3-8ad07caa6090	a496e647c7a5be98ee099f00758b72fe1459f8312b64369d33d7ac30f95c8d4c	a147a3e6075859462e98648da8c469c8bd220c3b036b042df19d654552bcd82a	2026-09-22 01:45:00.25618+05:30	2026-09-29 01:45:00.342254+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
a6de062e-4f9d-419b-b398-94d4f72ab8fe	de526836-5e73-49d7-9be3-8ad07caa6090	ec15e7e9f8b0c74bf0b812cd661443546e74c446671714b0d7ce3ad3910638c6	32221db1c620d5605ba2f2198e630033a8938e8504156afabdb43bb5fab73fe9	2026-09-22 02:58:09.757714+05:30	2026-09-29 02:58:09.810009+05:30	2026-09-29 14:26:28.612116+05:30	\N	103.171.172.134	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
d22adcb4-4732-48fd-90a5-ab61dad04761	de526836-5e73-49d7-9be3-8ad07caa6090	345f1ca130628a4658564900ab31e62c89dc2f91cea3626efa70988af02ed6f4	a235dec7de478d8ccee60b65908be45d5a37d829ef787044b5cd5eef28694b23	2026-09-22 11:26:35.493582+05:30	2026-09-29 11:26:35.559038+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
216a4075-4b30-4ca1-9465-b5f0e72f2e7c	de526836-5e73-49d7-9be3-8ad07caa6090	f3973f360b218908af1f732c7bb4b10f0da9eb77c9ae375646c8a369408ccfd8	d8b56021655244d9a3b4ac145c8b56d90b3f1242cbc33fe31cef4fb0d8bc9fcd	2026-09-23 00:32:43.821755+05:30	2026-09-30 00:32:43.877068+05:30	2026-09-29 14:26:28.612116+05:30	\N	103.171.172.132	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
ed39f036-7c8c-4bf6-885e-4d5b735e57ee	de526836-5e73-49d7-9be3-8ad07caa6090	fa2c98f005bdff893e25e9aac3cb05fa1a0eabb62ee316024dabd1c936a34bbc	35bd112b25ff7bbf616c12259c63ad2a8e88bc5f40d67b1fd8d91d437da27f8c	2026-09-23 01:46:35.205609+05:30	2026-09-30 01:46:35.26906+05:30	2026-09-29 14:26:28.612116+05:30	\N	103.171.172.132	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
873edfc2-3a0f-4fca-bb7a-7707cdd80d91	de526836-5e73-49d7-9be3-8ad07caa6090	2c0e03127d6003bc9f335b12186b1656b07564990999a16a9cfeadd5c250a5ec	230b7826e3635c98b2124056c63b65c81f3d67e53bdcc80fb5c99a644da26c9d	2026-09-23 15:38:36.245423+05:30	2026-09-30 15:38:36.313955+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
6c6574bd-2812-4c6b-86ce-a26045dad485	de526836-5e73-49d7-9be3-8ad07caa6090	1e83b6111cf069fd89962688b9f1d782a440c86c0908f9e60fcf6f2c8a0a934e	4e97ac495dc7ea735fcb3ca018833c33d8bbd81202d474e12de7cf3b4c34c53a	2026-09-23 17:54:49.652743+05:30	2026-09-30 17:54:49.723765+05:30	2026-09-29 14:26:28.612116+05:30	\N	2401:4900:8811:109b:e015:265:f23d:eab1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
d4b137ac-d43e-4fd2-b151-6eb828bcb44b	de526836-5e73-49d7-9be3-8ad07caa6090	4bdca4c7cf49c8fd15db4b97b625be76fa323e292919b48b254968e1deb5462e	2450baade237c381df3568df4ca9eeef44bb823044a71b0efaf4ba138490b1af	2026-09-23 23:38:17.171685+05:30	2026-09-30 23:38:17.225925+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
761d3a9a-0150-47e6-96f8-91d54494b14a	de526836-5e73-49d7-9be3-8ad07caa6090	6de864fcdc636357d03e9eae4268509abd17e0980c6f0db5259ad94a1b936a89	07ab9a5ef184cdc29587230368b27c1830e0105b4ecb0ba68298222121a15d89	2026-09-24 01:36:02.802224+05:30	2026-10-01 01:36:02.876063+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
ec84abb7-9f17-4b5e-a9a7-17d49476211c	de526836-5e73-49d7-9be3-8ad07caa6090	b988cebaaaa1375e5a6fb2d6f2e418200f3529a24c9982c5f91a1875efa1abbb	416cb58ceea9500f46b00fbdd2f08821e3f61bd0c3df376b6efe25230899eabb	2026-09-22 01:13:06.974622+05:30	2026-09-29 01:13:07.046468+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
31107cba-da97-4d2e-9793-5e8a8ba1c0f9	de526836-5e73-49d7-9be3-8ad07caa6090	cb4257aab87005fefd544c60d4e07bff0090a03a69d3299875b8a8428d769698	d22c2addf306ca0d8c136002d260f9ac92636b17d359487d2435a40e2e583c64	2026-09-21 01:51:36.076715+05:30	2026-09-28 01:51:36.149696+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
530f4193-b49c-4557-bdef-179a7f47f72f	de526836-5e73-49d7-9be3-8ad07caa6090	1c61a6e32bf8020e8bbdea8381b694059cc019ceb132ce38a7d92bb0e3106bd2	a1d2e01e6c11d616e9e49f47c553c96f51e014ec3503a35cee8e019acb7f4163	2026-09-23 01:00:50.662732+05:30	2026-09-30 01:00:50.730084+05:30	2026-09-29 14:26:28.612116+05:30	\N	103.171.172.132	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
59103a51-ac61-464b-ba49-f4fc7f948aa2	de526836-5e73-49d7-9be3-8ad07caa6090	efbbfb5733541dd119cb5fc6856db2af8311bf6564c78045872020f0508c9ad9	01ec4e55b95dbe17097ad15e8f2b4a080fc92b794c15692c1ec052e606593abd	2026-09-23 02:08:25.672499+05:30	2026-09-30 02:08:25.724029+05:30	2026-09-29 14:26:28.612116+05:30	\N	103.171.172.132	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
4b16b30e-9a71-47cd-860d-a96b82657bc7	de526836-5e73-49d7-9be3-8ad07caa6090	5c0dd7256022967e69b81a07b03d3bc060767e540d561017eebb5daa3b4ffd36	c4774a7aed0f45977377f409252b212bcfd2073d0eed6c2230e2a4d087cca53d	2026-09-23 16:21:02.003806+05:30	2026-09-30 16:21:02.076472+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
ce367ea7-5068-460e-9f90-47f74965d89e	de526836-5e73-49d7-9be3-8ad07caa6090	d32d954bfa25d56bce64ae4699437b21b6bf979c40a7ac972a97fe7c4579c3ef	98cf285311858707a46d3fc36ef6a365e45971d2dabfaca4074df9a273450913	2026-09-23 16:51:29.13336+05:30	2026-09-30 16:51:29.213565+05:30	2026-09-29 14:26:28.612116+05:30	\N	2401:4900:1cd6:6f51:4159:4706:5f92:7ca8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
a2c61b40-155b-43d8-86f4-49a248b3a2f9	de526836-5e73-49d7-9be3-8ad07caa6090	908cb94b8e468b9d927fe9d72954b96fb484a1f3e31e7cd66af593949976c6f1	441b172074d98d614c2b63f5851c0c81c8855e95f24b2814bb2e99415f0eebb5	2026-09-23 18:04:24.644599+05:30	2026-09-30 18:04:24.712807+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
16b8d3a1-9df8-44d0-9ae9-c232523b48da	de526836-5e73-49d7-9be3-8ad07caa6090	cfe2f1352f534927268ca1bb379fceeeeeaf2b1124f975760f61260e2a041ed5	3d59674a4137cedb74a6dba24bd4f212798ec9ac3969039d7b050b0adb555ebf	2026-09-23 18:41:32.861838+05:30	2026-09-30 18:41:32.934456+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
b5d65409-b6fd-422b-b5f1-ac8319ad3414	de526836-5e73-49d7-9be3-8ad07caa6090	a3308a2905d9a4bd432708d8c4c4d0b65012d665fbef26cf4a95ffbf6bd98f45	5dfc8e6137d0ed5dd3c12e90d640cc593fe046a280bda2e3c6246cc665844fa9	2026-09-23 22:44:23.842165+05:30	2026-09-30 22:44:23.892486+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
5c2287df-9ca9-4d2e-a76f-16097ef11250	de526836-5e73-49d7-9be3-8ad07caa6090	df9d3889c778f52f268a6fcd0207bdcaaa7eba1f7ce73922b8b50c3975e3f1ce	91c6be7e53ff3815d9a23c628f8cfbaf77b80a4609ffb15077f68aedeeb58069	2026-09-24 00:01:38.220205+05:30	2026-10-01 00:01:38.272105+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
12d0aaa0-2316-4966-9a5b-7f8449e918b8	de526836-5e73-49d7-9be3-8ad07caa6090	5dcd43a2d54d90a29323ef5dff28e2d24a2c8b209234b1307612e868d46d827d	20b90309b2089757fbf1fce29ec09d8600724b745d73684cf5c983569a1cf6a6	2026-09-24 01:00:48.391316+05:30	2026-10-01 01:00:48.462012+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
63b94b7f-a3eb-40a1-a335-31cd0914ee77	de526836-5e73-49d7-9be3-8ad07caa6090	50354ca4f6322e7bead22cd4c94aa133a72493d6247e4abed9517c4ef63abf56	30c8fbefa2c7d9d495cb903d5519eac3365ec9f9103f281237c91603dbe5f79a	2026-09-24 02:11:23.522486+05:30	2026-10-01 02:11:23.573849+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36
9ce98cbc-ab12-46f9-8cea-d087259c39b2	de526836-5e73-49d7-9be3-8ad07caa6090	c751209fa763bc9be01903687571108d26806cab0719c27ea303cdd27c66369b	45ceef0faa45940970327f0151e47bc79096b2bdf8fcac52750bec372df426e1	2026-09-25 11:07:58.703945+05:30	2026-10-02 11:07:58.772505+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
eb3e53d8-0dad-46da-9050-68c7e0634bcd	de526836-5e73-49d7-9be3-8ad07caa6090	6e70976c0472e1e3aa55bdb0df66e0b0ff0a7c7fb3d0899227b6cbad745cc84c	af77882cc0ac76e3c678bf3baf47e9fccf759e720eb4b719cb0c9f81847c89d2	2026-09-25 11:36:22.615929+05:30	2026-10-02 11:36:22.693875+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
78fd9290-c84f-4eae-aaa0-5b2524b73f8c	de526836-5e73-49d7-9be3-8ad07caa6090	12769ef9af78a887cee77beedc2f9565ff0c4e41535a32c8f35a8bbbc5a8c273	e7f37305414ea0a060e5a371fcb430d3ca8333794d2124ae594d542bdce06375	2026-09-25 14:03:18.128161+05:30	2026-10-02 14:03:18.190929+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
fd7701cc-ba1a-47be-beb0-697c46c41076	de526836-5e73-49d7-9be3-8ad07caa6090	856c92c9febf1fb62d9b72d0bf466fbae82ad8e6e306585f58af7bdc6680727f	6e1828ae6a557b54cdbd722a0a21ebdd2d865d41e141959a5207c251047423a6	2026-09-25 18:49:00.175004+05:30	2026-10-02 18:49:00.228588+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
470bf443-396b-4d32-b512-862bc45245e1	de526836-5e73-49d7-9be3-8ad07caa6090	e5ce1091018c6a6169467fd5916197b2f6ba0bbd9c8be69d0faf2201b1aaffca	b538fe1a5b123305e3699adc41e9ce4800c0240d2f9b839d3f986887f4368f42	2026-09-25 23:12:30.128373+05:30	2026-10-02 23:12:30.20086+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
68887828-80a0-4fab-b060-586aed850de0	de526836-5e73-49d7-9be3-8ad07caa6090	477c6e011b785465d62769d8b019c8ad4098714012ab6b2c5ca8b98b63278ba0	f8beeea2b3c07630aed0185b32c0f0efb33ef766530859b3c1c32dd417795e80	2026-09-26 00:34:27.21049+05:30	2026-10-03 00:34:27.270235+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
ce70a012-7ef2-4160-a68e-4951d6c5267a	de526836-5e73-49d7-9be3-8ad07caa6090	0f1615483becf4096705a01713ff2b476fdbdb017bc2a8206470db7633275057	dbac4d3d6e55c5a473dd2fefb310a8116db45180a0ae4c938b477b3adad02404	2026-09-26 01:16:07.80602+05:30	2026-10-03 01:16:07.865581+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
318bc3d3-b6fe-4a53-afcc-eced6576c6b1	de526836-5e73-49d7-9be3-8ad07caa6090	02f2e6891e3de509d50d7790d74c415cfd8eee68f7e7647b3158d5860c667578	846ed485ea7ca0623103d21e9c129af40b79e0079ac79b3c428c8b1210a89390	2026-09-26 01:50:39.881292+05:30	2026-10-03 01:50:39.934262+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
77893aae-d23e-4975-b518-c098b18ea2bb	de526836-5e73-49d7-9be3-8ad07caa6090	2dbaeebf8b240eea9a6ec3c0f2d13f7515644fa2e852c3f61dd0b0ad58d438a8	74e08caf8ef91949a4052d1d41c86a82c4147f95bbb73b810c20cd7a5b823a03	2026-09-26 02:13:20.879727+05:30	2026-10-03 02:13:20.93775+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
7b7e0d39-a254-415c-986b-b848df217d2a	de526836-5e73-49d7-9be3-8ad07caa6090	e1b6e5de62fdc901789298006a1225089ba46767482f76ed0a9cc2caf5ee30e2	cde2ad42f8dd2c932f833bd9d492ac01e22e0698ac756d89ccf8a4cfe15545b4	2026-09-26 11:58:48.453364+05:30	2026-10-03 11:58:48.54242+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
fb22837c-0147-4dc2-9339-57af58710b5e	de526836-5e73-49d7-9be3-8ad07caa6090	ae0bf0ff1b3bf756d8bffaafb17eae075aacccc81ae34130f0e895add33ec991	a03c87683fefe391bff2eff471f14d98423476f4750c82eb3c5dd31d978fd2ae	2026-09-28 18:23:47.077751+05:30	2026-10-05 18:23:47.162643+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
c83c847e-380e-4fdf-b90d-126cb10464a0	de526836-5e73-49d7-9be3-8ad07caa6090	7482c5e115c163ea1ced875aa491758a098d52024d91e2ee632ec5dd314ff919	1b4e1ca8aa53c5afa432d8a408350fd1bdbc8b129f0d70c3add01364463544be	2026-09-29 00:18:15.496592+05:30	2026-10-06 00:18:15.587883+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
4e40598e-5e95-4ab7-9158-99e4e33176d4	de526836-5e73-49d7-9be3-8ad07caa6090	f95fdff5b75acae7c13c73be3b10d37894634a764aa47fab42ae156dd5c7f08c	bac29140763e644f598274a6c8d43b3c4168c2e9ac9819b39960af5db5f74251	2026-09-29 00:37:03.15545+05:30	2026-10-06 00:37:03.243399+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
746d14ae-f4b8-40da-800b-5a3feb3ac08f	de526836-5e73-49d7-9be3-8ad07caa6090	2a17ecff5276c79b7378867822e30548675c2283a5307298177175900fce0678	28a6abe4a8e809f1a22ec71045fe56d61ca03c34b37074751c3ade1dfde260ef	2026-09-29 01:00:44.730879+05:30	2026-10-06 01:00:44.780585+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
2b9379b8-67c6-45bf-9dc4-18685facd22b	de526836-5e73-49d7-9be3-8ad07caa6090	cf86e957788673ee08fc00357cce3d1e83bb40c78c60783da287a3a5c8ad18a3	3985fea9cac8d31c1beee5c0b131e6e51f94fc0110f2b778991280a92d8fa907	2026-09-29 01:16:04.633469+05:30	2026-10-06 01:16:04.735637+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
97411468-3f55-41ed-a6c8-ea4396445e3c	de526836-5e73-49d7-9be3-8ad07caa6090	f8060abd1450d0848c5176b4b29efa287653b0d4b62449217e350324e8c8e5a4	742daf88443414f4eddc8c2ff795192b932c66271245b52e52f9a47e3b90c4fc	2026-09-29 01:31:19.742912+05:30	2026-10-06 01:31:19.819849+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
950e7ef2-4d88-4a8d-a807-7c60b463cf24	de526836-5e73-49d7-9be3-8ad07caa6090	f496dd0fec8f65328b2a87993c9f7814eae02a2bb8ff9c69d0fb69a7e717e49b	1d9e7ce7fa30ddb8c5d403189ad09402ce967222a7dba90cd99069fc5b1c60fd	2026-09-29 01:48:57.244889+05:30	2026-10-29 01:48:57.295709+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
3476320a-f389-4f88-9d00-de5a46c99ff3	de526836-5e73-49d7-9be3-8ad07caa6090	e37b2929a84dad934158ebe08394caad93fd883e280977d23e4b531aa928bbd0	fc544b9bb7ae6bb20ca09034e7f520a1ec5d65d72ff9cfa8f49ed3b17a38cef1	2026-09-29 13:55:41.182647+05:30	2026-10-29 13:55:41.255523+05:30	2026-09-29 14:26:28.612116+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
b318b43d-048a-4e3d-a2bf-ee79244498b8	de526836-5e73-49d7-9be3-8ad07caa6090	5a92aa10126fb353749444d408ab1e7ef1e91f031fa4cb3f160199b84e28439d	2d5c7103c3e7dd3d04bf3ce36faae3e0b2a55d3799c30d141b72ad606af90ff8	2026-09-29 14:30:45.736534+05:30	2026-10-29 14:30:45.804225+05:30	2026-09-29 16:50:17.898845+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
856ed53a-546e-4b5d-a2ed-645b2cd80f51	de526836-5e73-49d7-9be3-8ad07caa6090	26fd823317314a140248efae91ebe3a787908b081dac2f7fe6ef690b96e9f2a3	d094f4a834409786f95659aeeea4c3b0c4466d19270cb1dd4bfbed5aa2cefec5	2026-09-29 14:30:14.937917+05:30	2026-10-29 14:30:15.017281+05:30	2026-09-29 14:30:39.910803+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
441017bd-ca2a-4d55-aaa8-d6ea6a5c7445	de526836-5e73-49d7-9be3-8ad07caa6090	aec4ca1ad7f6d46ab64df18e62354b18b1449adf179ac706964c9f9bd22c91f1	d4df7d0c8c2e4ff731088d0836c966f5aabbcf16a0d3e58cade4f73fdcaa8d51	2026-10-10 01:25:40.593874+05:30	2026-11-09 01:25:40.604655+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
024eacbb-f3b6-4217-b1e8-ee6913d73346	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	508ca7879fc708cfca1697eb68e4b2dcfd47efb73ed711aa69e2479013cea8b0	b3fef1e2e8c5c902d03003e875faf77305e11e4cd792334f4b813e05da8ffd71	2026-10-10 01:26:00.360311+05:30	2026-10-10 01:56:00.367489+05:30	2026-10-10 01:26:16.089723+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
792cb2fb-f77f-42c2-90aa-231fa621421b	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	5d9494f45acf3f4648c26921cc9a6b8dd96b4fcc9d15e50c268dfe81c3b6ac1b	9b974ba2fd77195bd49577141dea2bfee1514596e167ef32c14ee081b6959413	2026-10-10 01:33:26.966489+05:30	2026-10-10 02:03:26.999401+05:30	2026-10-10 01:33:43.926488+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
8abf0d7d-6bb3-4cbd-afc9-57a5398e222d	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	dccc8059555adcfc9838361511881e58643b8a7a16c9b7ab9a5f8e21152ff2ba	da6020f74848ef56f15ff4e8b21e02d828b40e65f1e93a33faa7c8a02b338438	2026-10-10 01:34:31.884216+05:30	2026-10-10 02:04:31.889134+05:30	2026-10-10 01:35:51.572378+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
da652f31-65fe-4fc4-99cf-502eb53b6a02	de526836-5e73-49d7-9be3-8ad07caa6090	67e1fe51f9db2e689eeb58cc03188befd58992b91beb9eeaa58939686a610e65	abee81c70d155be5c0c29f59ff942ab10446ee09cf27c85c2d259d0fd11b26b0	2026-10-10 01:51:28.679382+05:30	2026-11-09 01:51:28.684151+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
ab9aa4fe-9c78-40c4-9e85-1276edf70936	69984504-68fe-470a-9240-4a37edf511b8	b0a42157b64d2cee30dbc2e02c02060d80b63a7a9538db3d123dec0f63d57757	443be3ee1d107f9f107eaac0436f3ba9d43e6174d9dcddd2271ce1116fff3084	2026-10-10 02:00:01.044778+05:30	2026-10-10 02:30:01.053771+05:30	2026-10-10 02:00:12.672974+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
dd3fddef-a48a-4ced-93e9-c49191e5cb78	de526836-5e73-49d7-9be3-8ad07caa6090	13f1eda082cad9aba080d5391afaeb77dfbaff28ab2239eb8bce7c60a040cd64	4099346924d87dc6f30fd5940991fe117507132af07e9075fa8877018553a313	2026-10-10 02:39:59.736668+05:30	2026-11-09 02:39:59.750074+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
0630018e-f4aa-4b52-a2bf-f0165f29d18c	8554d145-bdd4-4ee6-b821-74b73cfe40bf	ca832996bcf875b6a79590b8f7ce5751d66c14df452a2e4886d079420f7add0c	bd314638cad0b02254378131c82311c95d44bcc0f1a8bd9c97bffcb159d45ee1	2026-10-10 02:40:11.116949+05:30	2026-10-10 03:10:11.120632+05:30	2026-10-10 02:40:48.717055+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
295d1e14-0768-4e53-95b2-017dfb52bb8d	de526836-5e73-49d7-9be3-8ad07caa6090	2d3ca8138e732fddc8a3b44a3daa87fec8931feebfadfcdea619d4514d37a793	eb8a59d371738a7f506b699799a157c558f504c96a50bee3bb2275f0924e348e	2026-10-10 02:41:05.333059+05:30	2026-11-09 02:41:05.423398+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
d0216c31-ff48-4800-ac74-667283a4e644	8554d145-bdd4-4ee6-b821-74b73cfe40bf	e1b5841c7386b29a350c160a7467d94d99c1bdc1eb79273126831c89a086499c	b65d4d66c4b31bfafa01c8fd04325179a558e51f87c3d4f9771349670eb93bc1	2026-10-10 02:41:20.020429+05:30	2026-10-10 03:11:20.027128+05:30	2026-10-10 02:42:43.113685+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
6c28b9fb-2619-43d2-a8cd-ac910686689d	de526836-5e73-49d7-9be3-8ad07caa6090	da99b88b95b0e0d30862bab0a037fc8399a1405563148287b2f3ff4e7c8fab8a	5bb228d8d72ac4223602125ce9effdac4dfb49d282a61769e2c2657a9b23e749	2026-10-10 02:42:43.106834+05:30	2026-11-09 02:42:43.118494+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
07fadb1f-47e0-4ac6-9bb7-2866f036aa3e	8554d145-bdd4-4ee6-b821-74b73cfe40bf	b65064e0572af6edd53d49f6f339e56ab5ee5f19b8e19f57caf11814e4b5a096	5b184e1592adc72a91ba8257db9e82b5ce0cb0fbd8d85ab8de10ebcadeb4e9ea	2026-10-10 02:43:41.57612+05:30	2026-10-10 03:13:41.583085+05:30	2026-10-10 02:45:00.650043+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
a187792c-4d6b-4fb5-a005-7348cc1bf2a0	de526836-5e73-49d7-9be3-8ad07caa6090	9b8607a2b7bf3da42739d21f743e24016375b8c98be4208b39b9bfa1e4afdcc5	a7af3ec44d4dde56f3a475a0d340263d5ed848f9d0875ad9dfcd5a4c27ad79a8	2026-10-10 02:45:00.645431+05:30	2026-11-09 02:45:00.652167+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
e4dd8b3f-7ea4-4bd0-a09e-35324f414fa2	65b43201-4875-4caa-a601-b0b535019b48	ec1b8358d841cbedfba3d769f148c96414cfe4f3f5b4badbbcd00b95025fea9d	eedc9811ae18172bb81d0a1538075e997514058956ebe59a0a1078052db7f051	2026-10-10 02:47:20.996785+05:30	2026-10-10 03:17:20.999264+05:30	2026-10-10 02:47:47.684475+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
0d424e72-841d-417d-8d57-c1983debe950	de526836-5e73-49d7-9be3-8ad07caa6090	7bc814461f172b319836ad5d1a9b1e7b38bbdccec9d5f7c27be92a87b3bcd4c0	7936bd91c6f7ef013cd38f3dd2b7789a02f3ecfcddd448b442c3095228b98579	2026-10-10 02:48:02.631033+05:30	2026-11-09 02:48:02.689155+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
c4db9ccc-fbf6-440b-aea7-851acfabec26	de526836-5e73-49d7-9be3-8ad07caa6090	4c98e8b2644782ca3998c8ee45f487f266367007cdb7d4d84220fb2aedc30de3	fcabe7afb56076e0dfb989cf96f40cafe0bbd61278c9d1f6041e8d16676290ce	2026-10-10 02:48:28.976053+05:30	2026-11-09 02:48:29.058562+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
cde47f15-b7f3-4000-95a9-a837fac35f03	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	3867236b48110b7150f902e59ab716a1f623d7d43166ad43e00f1a1836dd3f68	fa72af49c5addff7000416a6c898e26522c943040069ae741e6a5b15973285c8	2026-10-10 02:49:41.12829+05:30	2026-10-10 03:19:41.13809+05:30	2026-10-10 02:51:40.808383+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
0d9eb165-ece6-4add-bd83-f7ccaff89d18	65b43201-4875-4caa-a601-b0b535019b48	8db753e2498606788d5bbf9bc76a9f56cd3652c5720b4b159d28babcc3a0cd0f	a50b4ded890a496d666a516a4871d5c0edb2fa328fbe81fd0390ebbb290c4ac1	2026-10-10 02:48:37.156878+05:30	2026-10-10 03:18:37.159912+05:30	2026-10-10 02:49:16.607938+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
7237ec26-260d-4fd3-a18a-eab161f75bca	65b43201-4875-4caa-a601-b0b535019b48	d4e58117c68489eb4d6730d217e4000b48863e99e8f95c4d652cb873cf226c17	98a0a535a380a268685b1b340a5e61997897c6309a8bab3e3037853b005304c9	2026-10-10 02:51:58.692597+05:30	2026-10-10 03:21:58.69714+05:30	2026-10-10 02:53:48.241741+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
8c94b0fb-8d9b-4127-82b9-ae9c0957679c	de526836-5e73-49d7-9be3-8ad07caa6090	2e1b6ec5cde7aa9d9b18d67f375ada94d9d828e1b5932d8a5b02d970ae64aa01	4a500d312b62702586d8fb96a7e2e7a4b41abfa815fec14448c4a2ad9202cc69	2026-10-10 02:49:16.60133+05:30	2026-11-09 02:49:16.612551+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
022abf38-499c-4f78-9de9-e119c2384e4c	de526836-5e73-49d7-9be3-8ad07caa6090	3f04038f541817950916a28ae2ecff88634badb71e8a3d99efd24b5318eb5677	59690fbd29a16f7d8432e7b8e70089b9518168590de5235ef659ee41c98a63a4	2026-10-10 02:51:40.796536+05:30	2026-11-09 02:51:40.813808+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
80b4bebb-18cf-4657-8a0f-04c814f5afae	de526836-5e73-49d7-9be3-8ad07caa6090	c521e4becb7e7ef71f9d12d6af4a392aa9565408aaa9314de595434420320464	93b82ae48e8af22ba6dfb12d5a2c9107a3af2789621e608e2e01e37a974e36a7	2026-10-10 02:53:48.233548+05:30	2026-11-09 02:53:48.248157+05:30	2026-10-10 14:03:37.497088+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
5ad607c8-72d1-4f49-926d-740268d65dd3	de526836-5e73-49d7-9be3-8ad07caa6090	ac6cbbecda887203e2ea58df3ba6bdeb4efacb72ac544503e26c27978a3b5e42	765b2c3230a585f2d9b38173561a1286f0f328dc3ee08fb42d5e2c0750a6273e	2026-10-10 14:04:00.784374+05:30	2026-11-09 14:04:00.856867+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
48a37278-a2b7-4961-b517-d7757039c56d	0438f197-65cc-4fb2-8667-bdaceee1db81	9f939c55e0548c7c927cc2822214048a8b7fbd25b7918909f5203ced7227f18e	a6d153f6390a0fab3ebd1c3a0196fc4da5444483ef664b8be2163a1c85309ac0	2026-09-26 00:13:50.952282+05:30	2026-10-03 00:13:51.020996+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
20e053d8-00cb-45ea-89e5-8ea595d961df	0438f197-65cc-4fb2-8667-bdaceee1db81	a8d1a1afa1964654fef73ec7658f463b4dedb5efcfc371446ff2fc3cbb204a72	396ed13a2a2fe348b2c0b2ea84826bd6db3a3e009efe0dd0a8aa05f3dbd06c46	2026-09-26 00:47:20.073848+05:30	2026-10-03 00:47:20.153092+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
2387d41b-70f6-49aa-a7d1-98c3241259a7	0438f197-65cc-4fb2-8667-bdaceee1db81	595482669776e9a99ffc93c744794d2f21f63300c3dbb0d039fa8769fda45780	0e0a8b57773c4134a7bc6d37dd20e53d707c33dfc7a121f5733ee889d1370c16	2026-09-26 01:28:42.289733+05:30	2026-10-03 01:28:42.357849+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
3f1e8ddf-3e82-4d77-927b-f66c62658af9	0438f197-65cc-4fb2-8667-bdaceee1db81	89080a1ad73e8bff5e4440608c9fac55a94cd40e2b9e970ffd3d480a5ca92e77	e84a67c3f4793c410a3e6866b7954891fdeaed8cc4cb0ecf3448bb86957b41ae	2026-09-26 01:51:07.989276+05:30	2026-10-03 01:51:08.041829+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
5926ea66-b95f-4d80-80cf-d78ba64c35e4	0438f197-65cc-4fb2-8667-bdaceee1db81	2cc9ee1731722df1461d5b1bf3c8d85eb58ddd6b1a8ade882c1349d1edb39682	da9850d0f4fe8fd45072bf686a6466059228fdf60e20e3a6157d72b3a9c5000f	2026-09-26 02:13:43.420007+05:30	2026-10-03 02:13:43.469702+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
38a3d18c-c376-4f40-9e22-170a66d28a98	0438f197-65cc-4fb2-8667-bdaceee1db81	82d0391009d2d3afc01ad23c6604106075e9f55d4f15a0149984d3f6e4a6c80a	b47862180987e82fd581878b58ebc2ca0a8abb9f49d3450220405f7eb75f015d	2026-09-28 16:01:41.414197+05:30	2026-10-05 16:01:41.488101+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
96d4452f-c3eb-4c93-a8f0-b2fc24bdc127	0438f197-65cc-4fb2-8667-bdaceee1db81	10b10a497cc17898faf0d835c59edead49dce433b68b8a1a396dc78a011b5c0a	0e9d439008a44df08cf42822bb74b9e0b7be61804a709f387ed664d786621ff5	2026-10-10 14:28:36.443498+05:30	2026-11-09 14:28:36.517178+05:30	2026-10-10 14:28:59.012932+05:30	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
faee0b75-6037-41cf-84e3-df5fe6eb87a1	0438f197-65cc-4fb2-8667-bdaceee1db81	78e266a80c337c2e790f785eb789f90f63612e69c7453099aa646a7cbecbea76	ade5a5afec739de5f0981ff55681000b6f0f9c556eb27b938e90bc5bd7a8cf44	2026-10-10 14:29:18.057963+05:30	2026-11-09 14:29:18.121123+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
ad62dcfc-0cd7-4c43-88ad-43e0a8bccdcb	de526836-5e73-49d7-9be3-8ad07caa6090	d96d7f6dd9b4e05ff444e5a0aa2fccba31dfd5b7e3dd91900b4e68893c4049ef	7fa229088d3a5ca1a9a27fad8700163fbe4673da23a43d6588cac8b3eceb7152	2026-10-13 10:57:19.560396+05:30	2026-11-12 10:57:19.630416+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
a03f01f6-232d-42cb-a8e7-aad933bcc4ff	de526836-5e73-49d7-9be3-8ad07caa6090	be2a0a2363210c890352e7ee897526a124fc5560ec889b0e2ba71ce7fac2ef74	2a19243f705fe250e6accc0514f82105ffcd3a77166e31c0e28408ff036410d8	2026-10-19 12:31:15.339411+05:30	2026-11-18 12:31:15.405597+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36
62e67031-c295-4a9e-86a4-3ef769d07d54	de526836-5e73-49d7-9be3-8ad07caa6090	e8cb0fdcffb0054cfe1ceb141fadf46d619ee763cc17e1fb0d6be94812c61618	a2f8c804ced5ce044879043e9c90e746f49acc655f0215471711df830bf6810b	2026-10-24 22:40:00.232862+05:30	2026-11-23 22:40:00.34829+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36
06036f03-82f9-488c-af10-e3f7f9260fda	de526836-5e73-49d7-9be3-8ad07caa6090	adac717c020dc29ddd1421a43d2b45755461930b82eb53c6da3ca64ed6e5ebd4	c4972b0bb173c188ac95ac6a90acfa4949caab23dae88f6471a04807c6410b71	2026-10-26 02:48:09.800613+05:30	2026-11-25 02:48:09.876604+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36
bb0880ad-65f3-4691-95ab-3a16a2258897	de526836-5e73-49d7-9be3-8ad07caa6090	a97fbad47efcd2b141c4065886915ddd05f77e01dc401c3b722d3a5035f605b4	a9a1a6a6d96d058b997864f3e38453bd3c22785c75ed4cdcb7ebdac1652240cd	2026-10-31 12:05:45.426556+05:30	2026-11-30 12:05:45.507308+05:30	\N	\N	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
\.


--
-- Data for Name: client_master; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.client_master (client_id, company_id, client_name, entity_type, contact_person, contact_email, contact_phone, pan_number, gstin, city, state, created_by_user_id, status, created_at, updated_at) FROM stdin;
db62ec41-a44c-47fa-8baf-218673960742	5242338c-3887-56db-b86c-c59deae26654	KAPPER	INDIVIDUAL	KAPPER	9089090989@client.crm	9089090989	\N	\N	\N	\N	de526836-5e73-49d7-9be3-8ad07caa6090	ACTIVE	2026-09-23 23:42:54.314988+05:30	2026-09-23 23:42:54.314988+05:30
4973250a-e81d-4c05-8f20-93c83e86c635	5242338c-3887-56db-b86c-c59deae26654	LENSKART	INDIVIDUAL	LENSKART	9031999999@client.crm	9031999999	\N	\N	\N	\N	de526836-5e73-49d7-9be3-8ad07caa6090	ACTIVE	2026-09-28 15:58:28.190352+05:30	2026-09-28 15:58:28.190352+05:30
8d2cae66-0949-4781-9c3c-4a501aba928c	5242338c-3887-56db-b86c-c59deae26654	EBIKEGO	INDIVIDUAL	EBIKEGO	9031999978@client.crm	9031999978	\N	\N	\N	\N	de526836-5e73-49d7-9be3-8ad07caa6090	ACTIVE	2026-09-29 16:53:39.808136+05:30	2026-09-29 16:53:39.808136+05:30
a11df6a4-62e1-4193-9943-fc6940fc3cc5	5242338c-3887-56db-b86c-c59deae26654	Varun (EVTL)	INDIVIDUAL	Varun (EVTL)	9898897487@client.crm	9898897487	\N	\N	\N	\N	de526836-5e73-49d7-9be3-8ad07caa6090	ACTIVE	2026-10-09 19:27:56.209419+05:30	2026-10-09 19:27:56.209419+05:30
683e7249-ea02-409f-bdc5-fca7a8a7e415	46deca34-710f-5c79-83ab-939b03bffa22	lenskart	INDIVIDUAL	lenskart	9292123456@client.crm	9292123456	\N	\N	\N	\N	8554d145-bdd4-4ee6-b821-74b73cfe40bf	ACTIVE	2026-10-10 02:44:56.415556+05:30	2026-10-10 02:44:56.415556+05:30
6b1e36ad-e64c-4a55-ad31-c5622c26bf85	5242338c-3887-56db-b86c-c59deae26654	Demo	INDIVIDUAL	Demo	9031999975@client.crm	9031999975	\N	\N	\N	\N	de526836-5e73-49d7-9be3-8ad07caa6090	ACTIVE	2026-10-25 22:19:21.553027+05:30	2026-10-25 22:19:21.553027+05:30
\.


--
-- Data for Name: company_master; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.company_master (company_id, company_code, company_name, legal_name, employee_code_prefix, next_employee_number, status, created_at, updated_at) FROM stdin;
46deca34-710f-5c79-83ab-939b03bffa22	ENTERPERNERSHIP	Enterpernership	\N	EP	3	ACTIVE	2026-09-20 15:45:52.677412+05:30	2026-10-10 02:38:59.036886+05:30
5242338c-3887-56db-b86c-c59deae26654	GOCOMPLIANCES	Gocompliances	\N	GC	9	ACTIVE	2026-09-20 15:45:52.677412+05:30	2026-10-10 02:46:31.655795+05:30
\.


--
-- Data for Name: department_master; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.department_master (department_id, department_code, department_name, description, status, created_at, updated_at) FROM stdin;
a9593c21-af68-5071-9436-ee1f58930c3e	ADMINISTRATION	Administration	Executive leadership, administration, and corporate compliance operations	ACTIVE	2026-09-20 16:04:44.171071+05:30	2026-09-20 16:04:44.171071+05:30
2326fd8f-44f5-5b3f-8fbd-d11942c8404e	SALES	Sales	Business development, client acquisition, and sales operations	ACTIVE	2026-09-20 16:04:44.171071+05:30	2026-09-20 16:04:44.171071+05:30
996d9e8f-777e-5a29-a2fb-6feebbce6c1b	OPERATIONS	Operations	Client fulfillment, compliance services delivery, and casework	ACTIVE	2026-09-20 16:04:44.171071+05:30	2026-09-20 16:04:44.171071+05:30
f6bf4872-0388-5573-9c1d-8703a128ff45	RND	R&D	Research and development, technology solutions, and regulatory analysis	ACTIVE	2026-09-20 16:04:44.171071+05:30	2026-09-20 16:04:44.171071+05:30
4369d882-ba37-4dd6-931c-8d96d6a8e7e4	ACCOUNTS	Accounts	Accounts	ACTIVE	2026-09-29 23:07:32.588942+05:30	2026-09-29 23:07:32.588942+05:30
\.


--
-- Data for Name: designation_master; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.designation_master (designation_id, designation_code, designation_name, level_rank, is_managerial, description, status, created_at, updated_at) FROM stdin;
b15c7681-9eb7-5751-a553-82dcd245b163	EXECUTIVE	Executive	10	f	Entry-level operational and executive position	ACTIVE	2026-09-20 16:38:29.273641+05:30	2026-09-20 16:38:29.273641+05:30
2477adb3-666c-55d9-81e8-1f925f729d5e	SENIOR_EXECUTIVE	Senior Executive	20	f	Experienced operational professional handling complex workflows	ACTIVE	2026-09-20 16:38:29.273641+05:30	2026-09-20 16:38:29.273641+05:30
08dff813-b33d-5afc-88f8-a90ae8ee77d4	ASSISTANT_MANAGER	Assistant Manager	30	t	First-line supervisory and managerial position	ACTIVE	2026-09-20 16:38:29.273641+05:30	2026-09-20 16:38:29.273641+05:30
df74d857-6fc7-5dc9-b085-667b5eed5e43	MANAGER	Manager	40	t	Functional team manager responsible for operational delivery	ACTIVE	2026-09-20 16:38:29.273641+05:30	2026-09-20 16:38:29.273641+05:30
eabd6622-4960-5a04-862d-743ad60abeac	HEAD	Head	50	t	Departmental head leading strategy and departmental performance	ACTIVE	2026-09-20 16:38:29.273641+05:30	2026-09-20 16:38:29.273641+05:30
91482014-6f86-54a6-beeb-cce2557dc001	DIRECTOR	Director	60	t	Executive director overseeing company-wide business verticals	ACTIVE	2026-09-20 16:38:29.273641+05:30	2026-09-20 16:38:29.273641+05:30
\.


--
-- Data for Name: impersonation_audit_logs; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.impersonation_audit_logs (audit_id, session_id, actor_admin_id, target_user_id, action, details, ip_address, user_agent, created_at) FROM stdin;
fe457812-c306-4f2e-82ed-cda8caf00d32	72a4a8a9-66ed-42cf-a990-afb52af4901a	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Karishma Upadhyay", "actor_employee_code": "CG0001", "target_employee_code": "CG0004"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-07 02:23:27.870745+05:30
b1847598-2582-4138-8fb7-5e5dfa69641c	72a4a8a9-66ed-42cf-a990-afb52af4901a	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "CG0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-07 02:23:46.96456+05:30
2da8cb25-aa69-4daf-b382-a51a672a92a8	8f1c122b-53ea-4cad-8203-9f6b4644753e	de526836-5e73-49d7-9be3-8ad07caa6090	0438f197-65cc-4fb2-8667-bdaceee1db81	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Deepak Kumar", "actor_employee_code": "CG0001", "target_employee_code": "CG0005"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-07 02:24:23.141344+05:30
feb64c78-6f5e-4eb7-95f7-d68ca26c8fda	8f1c122b-53ea-4cad-8203-9f6b4644753e	de526836-5e73-49d7-9be3-8ad07caa6090	0438f197-65cc-4fb2-8667-bdaceee1db81	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "CG0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-07 02:24:33.446266+05:30
692ffd84-75d6-4031-8595-b3403e0f7aa5	605844a4-03e9-443c-ac66-96990f2520ee	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Muskan Gupta", "actor_employee_code": "CG0001", "target_employee_code": "CG0002"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-07 02:24:44.837085+05:30
3b9e148d-7190-493c-898c-ab4d887b0670	605844a4-03e9-443c-ac66-96990f2520ee	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "CG0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-07 02:24:47.827591+05:30
ad807ea8-45dd-4328-8551-adc6510b9c09	45461d28-6eb2-45c9-830a-d6a26d4c82f9	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Muskan Gupta", "actor_employee_code": "GC0001", "target_employee_code": "GC0002"}	\N	\N	2026-10-10 01:24:28.951398+05:30
ac33f28f-f1cf-4fd9-abd3-509fbfe0eef5	d4172bb9-d02e-46e1-84e9-b0f5f69c5a57	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Muskan Gupta", "actor_employee_code": "GC0001", "target_employee_code": "GC0002"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:25:07.225374+05:30
a5315dc8-9883-45aa-9592-2475b986531e	fa4917b7-82c8-4600-97b3-fefa6ad20f43	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Muskan Gupta", "actor_employee_code": "GC0001", "target_employee_code": "GC0002"}	\N	\N	2026-10-10 01:25:37.13063+05:30
61298acb-19d7-42c7-bb52-d5a9dcc92ed5	ad016f1c-c8dd-4200-8ad7-ab46f47d7407	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Muskan Gupta", "actor_employee_code": "GC0001", "target_employee_code": "GC0002"}	\N	\N	2026-10-10 01:25:37.163941+05:30
fd0a3ced-b783-4580-b0ae-9b5ab05af0b2	cb05017c-bd33-4bad-bf42-9bf5fd725fc2	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Muskan Gupta", "actor_employee_code": "GC0001", "target_employee_code": "GC0002"}	\N	\N	2026-10-10 01:25:37.169227+05:30
a5e81393-5a55-4c44-9215-dec71b1a346e	2808d885-6cb7-468e-bfcf-a46cd73193e7	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Karishma Upadhyay", "actor_employee_code": "GC0001", "target_employee_code": "GC0004"}	\N	\N	2026-10-10 01:25:37.178802+05:30
ac8e669d-40d6-45b5-8d21-1dea1cb06882	30f4e33c-8516-47fa-a312-3f1a1f2ad752	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Karishma Upadhyay", "actor_employee_code": "GC0001", "target_employee_code": "GC0004"}	\N	\N	2026-10-10 01:25:37.183048+05:30
00e93fd7-bf33-4584-9fa1-12507ec958a1	70448258-ce21-4e5b-b1d6-253e3a432748	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Karishma Upadhyay", "actor_employee_code": "GC0001", "target_employee_code": "GC0004"}	\N	\N	2026-10-10 01:25:37.188136+05:30
c7dd8aff-e127-4b23-9d0c-8a6b35640d29	71699d3e-b8e3-4f81-a0e2-a2eba8ef4338	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Muskan Gupta", "actor_employee_code": "GC0001", "target_employee_code": "GC0002"}	\N	\N	2026-10-10 01:25:37.194813+05:30
73c225a3-b28e-4f93-a9f8-e1fc33208297	d4172bb9-d02e-46e1-84e9-b0f5f69c5a57	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:25:40.59729+05:30
b4a20631-fb08-43ae-ba55-7b8cb75848b8	87e72aec-5ad1-476a-bd71-46f8aa192055	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:26:00.367265+05:30
a91a2e03-878e-4868-a236-23e8379de65e	87e72aec-5ad1-476a-bd71-46f8aa192055	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:26:16.089723+05:30
587808e7-919b-4ee5-973d-eb3bbaf28a63	0a7fcf9a-d7c8-4d06-83fe-5a5ae357686a	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Karishma Upadhyay", "actor_employee_code": "GC0001", "target_employee_code": "GC0004"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:28:36.244012+05:30
0ff841f0-9de2-4711-b31b-efb88451a0d6	0a7fcf9a-d7c8-4d06-83fe-5a5ae357686a	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:28:40.89817+05:30
622ee003-6504-4fa8-b227-a800cd95a7ac	4bde06d8-eba8-4e38-9a36-0fbf3d8c5047	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:28:55.090196+05:30
d55e0022-1dba-4883-ba37-8f02918b610f	4bde06d8-eba8-4e38-9a36-0fbf3d8c5047	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:29:31.057602+05:30
5b7b8a7a-8f54-4d85-b35b-b536c1a7c83b	99a2afe7-8383-4771-8127-e3dc62700622	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:29:37.473854+05:30
3666f039-5ee6-4f4c-8b51-5c6a3039d837	99a2afe7-8383-4771-8127-e3dc62700622	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:29:56.372696+05:30
96a7506e-7bbd-48a9-9411-04dbe6c47189	d75bbaa1-39ec-4be5-9448-99383a90ea6d	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:33:26.998581+05:30
0266fccb-51fc-44ec-82c1-c0d354c58593	d75bbaa1-39ec-4be5-9448-99383a90ea6d	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:33:43.926488+05:30
f05c301d-be59-4e29-a798-0925fe70d9f5	8d483284-9042-41d9-ab2d-7cd33de7b6c7	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:34:13.633383+05:30
9fcee4e2-5386-42a2-a227-ee9277204201	8d483284-9042-41d9-ab2d-7cd33de7b6c7	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:34:28.830545+05:30
77feb748-7f09-4d1e-a460-5fd124889de2	2dbc7195-1f27-444d-8f6c-8e4182fa68d6	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:50:26.475765+05:30
5b85d91d-4b58-4233-9c8a-2570c8720c16	3e467eb0-f7ed-4b52-903c-3df32b9bcf49	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:50:54.264275+05:30
90afe6ac-db07-4fb0-ae28-95a35d3fda2a	3e467eb0-f7ed-4b52-903c-3df32b9bcf49	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:51:19.34247+05:30
ecd43eda-27d8-4f4e-b062-3290b10e266a	59966aae-45e3-4aa9-856a-76dbb59332a2	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:51:22.961208+05:30
a27296a0-3e22-4ea0-81bc-e488cce44e45	c22ac9e4-03bd-42cb-95ae-2e6372f45def	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:53:33.753772+05:30
af647e84-b719-46c7-a926-4bdb206686d5	f42bf964-bb3f-479e-ab73-50e2ac0ff470	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:34:31.888815+05:30
c5795558-ade6-48ff-88ca-f66cad5f98be	f42bf964-bb3f-479e-ab73-50e2ac0ff470	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:35:51.572378+05:30
95d6b2f0-ca38-4ecf-8a6f-fcbcdbeacd62	4594f41f-6b51-4b48-ba9d-8ee15f3f4cd4	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:50:04.07851+05:30
7294f678-4718-40a5-bb2a-1d04f2e41a77	4594f41f-6b51-4b48-ba9d-8ee15f3f4cd4	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:50:17.169461+05:30
bf2eb59f-f9ab-4dda-a2cd-927ba9422171	2dbc7195-1f27-444d-8f6c-8e4182fa68d6	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:50:39.584321+05:30
43afe8dc-587d-4b74-845a-4bec357e2278	59966aae-45e3-4aa9-856a-76dbb59332a2	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:51:28.682019+05:30
8a04fcb3-bfbb-49e0-aca9-91507d2ef5c2	c22ac9e4-03bd-42cb-95ae-2e6372f45def	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:51:31.760121+05:30
34951723-df0b-4769-87b9-1e53770a338b	ccdc67e1-712b-477e-8848-440499d2139c	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:59:02.921048+05:30
ee8cc589-a85d-4529-8224-f778f1966b53	fee7382e-64bd-4e89-809f-55e49a3e614b	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Karishma Upadhyay", "actor_employee_code": "GC0001", "target_employee_code": "GC0004"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:59:13.310591+05:30
95f62988-1a13-49db-9c21-585eaff425fc	78492e57-fbce-4695-98ad-e9f0a09158e2	de526836-5e73-49d7-9be3-8ad07caa6090	0438f197-65cc-4fb2-8667-bdaceee1db81	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Deepak Kumar", "actor_employee_code": "GC0001", "target_employee_code": "GC0005"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:59:29.998019+05:30
f252e09c-d7bc-46c8-8dee-c5dcc1e256eb	e6b548f1-fb83-4cd5-98c7-f7b78f197d09	de526836-5e73-49d7-9be3-8ad07caa6090	4ce61bc1-113e-42e4-a934-c58c9d61e541	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Arun Saini", "actor_employee_code": "GC0001", "target_employee_code": "GC0006"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:59:47.812868+05:30
e652fdc1-4842-4045-a046-d0f2ff61ba74	bb47893b-2e7f-4e0f-a655-70fb2a828a24	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Muskan Gupta", "actor_employee_code": "GC0001", "target_employee_code": "GC0002"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:00:01.053579+05:30
908ffabd-336b-4cba-b192-b290cf92d8f0	bb47893b-2e7f-4e0f-a655-70fb2a828a24	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:00:12.672974+05:30
f61485e7-d5c0-4742-bae4-992f33d9ff20	85fa0aaa-e571-4954-ace6-5ff5de1ada1a	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:39:40.476337+05:30
af33b0e0-456f-4bb8-a630-662fce724a93	85fa0aaa-e571-4954-ace6-5ff5de1ada1a	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:39:59.745704+05:30
ae715599-d6f4-41e7-bd84-9141b2f37a17	7122bb84-41f1-4f5e-8458-76827c082ca0	de526836-5e73-49d7-9be3-8ad07caa6090	8554d145-bdd4-4ee6-b821-74b73cfe40bf	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Reeya Soni", "actor_employee_code": "GC0001", "target_employee_code": "EP0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:40:11.120458+05:30
2153b2da-886e-4b09-b3a4-156e3382320b	7122bb84-41f1-4f5e-8458-76827c082ca0	de526836-5e73-49d7-9be3-8ad07caa6090	8554d145-bdd4-4ee6-b821-74b73cfe40bf	IMPERSONATION_END	{"reason": "LOGOUT"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:40:49.98121+05:30
0d09b6e9-fd9b-46c1-a57c-69311d54cd45	24af7cbb-89c4-45e8-a785-0fb08c78c038	de526836-5e73-49d7-9be3-8ad07caa6090	8554d145-bdd4-4ee6-b821-74b73cfe40bf	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Reeya Soni", "actor_employee_code": "GC0001", "target_employee_code": "EP0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:41:20.026809+05:30
5469fe2e-55e3-4c97-86ef-1296532dcc16	24af7cbb-89c4-45e8-a785-0fb08c78c038	de526836-5e73-49d7-9be3-8ad07caa6090	8554d145-bdd4-4ee6-b821-74b73cfe40bf	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:42:43.113685+05:30
1b77aca2-a539-48f2-b42f-a3e1be741f26	fad7a542-53e5-41f1-9902-c72ec3d13d2e	de526836-5e73-49d7-9be3-8ad07caa6090	8554d145-bdd4-4ee6-b821-74b73cfe40bf	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Reeya Soni", "actor_employee_code": "GC0001", "target_employee_code": "EP0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:43:41.58195+05:30
dd0bbfe3-6945-4351-bbc2-24e95b885f2b	fad7a542-53e5-41f1-9902-c72ec3d13d2e	de526836-5e73-49d7-9be3-8ad07caa6090	8554d145-bdd4-4ee6-b821-74b73cfe40bf	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:45:00.650043+05:30
4d1c249d-5955-4664-9878-19d99de429de	72fb2382-ac9c-405f-92af-093d0045eb8f	de526836-5e73-49d7-9be3-8ad07caa6090	65b43201-4875-4caa-a601-b0b535019b48	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Hrithik Choudhary", "actor_employee_code": "GC0001", "target_employee_code": "GC0008"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:47:20.999117+05:30
801367d2-0ef5-4cfd-a07e-572f80917d38	72fb2382-ac9c-405f-92af-093d0045eb8f	de526836-5e73-49d7-9be3-8ad07caa6090	65b43201-4875-4caa-a601-b0b535019b48	IMPERSONATION_END	{"reason": "LOGOUT"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:47:48.943231+05:30
d136f3e9-a649-40fa-a4ab-f8793c9449cb	fb07934b-effa-411e-bc0b-812218e0c23e	de526836-5e73-49d7-9be3-8ad07caa6090	65b43201-4875-4caa-a601-b0b535019b48	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Hrithik Choudhary", "actor_employee_code": "GC0001", "target_employee_code": "GC0008"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:48:37.159734+05:30
face3ba5-c92e-4a1d-803f-40902d810d53	fb07934b-effa-411e-bc0b-812218e0c23e	de526836-5e73-49d7-9be3-8ad07caa6090	65b43201-4875-4caa-a601-b0b535019b48	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:49:16.607938+05:30
f91b9e36-6796-42c0-bbae-b250568a3e39	5d0d1561-100f-4ce0-b3ef-e50c9f69757a	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:51:40.808383+05:30
0841dc7e-949d-4f36-89ba-60edb2bafabc	50ff37c0-33f0-4e0c-a182-3878951d2a43	de526836-5e73-49d7-9be3-8ad07caa6090	65b43201-4875-4caa-a601-b0b535019b48	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Hrithik Choudhary", "actor_employee_code": "GC0001", "target_employee_code": "GC0008"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:51:58.696461+05:30
6e5bb0d2-efa7-4b19-b290-19c00713980f	5d0d1561-100f-4ce0-b3ef-e50c9f69757a	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	IMPERSONATION_START	{"actor_name": "Super Admin", "target_name": "Mansi Singhal", "actor_employee_code": "GC0001", "target_employee_code": "GC0003"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:49:41.137891+05:30
75adba32-f3e7-4382-8d7a-78d4361a8a81	50ff37c0-33f0-4e0c-a182-3878951d2a43	de526836-5e73-49d7-9be3-8ad07caa6090	65b43201-4875-4caa-a601-b0b535019b48	IMPERSONATION_END	{"reason": "RETURN_TO_ADMIN", "actor_employee_code": "GC0001"}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:53:48.241741+05:30
\.


--
-- Data for Name: impersonation_sessions; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.impersonation_sessions (session_id, actor_admin_id, target_user_id, impersonation_token_jti, is_active, created_at, expires_at, ended_at, ended_reason, created_ip, user_agent) FROM stdin;
72a4a8a9-66ed-42cf-a990-afb52af4901a	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	3b477cfe3995aef86631e399ce6ad634eaf3aff9a385a17f585d0aed5bd3363a	f	2026-10-07 02:23:27.870745+05:30	2026-10-07 02:53:27.870745+05:30	2026-10-07 02:23:46.96456+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
8f1c122b-53ea-4cad-8203-9f6b4644753e	de526836-5e73-49d7-9be3-8ad07caa6090	0438f197-65cc-4fb2-8667-bdaceee1db81	dcb54c2366faeca53245ed0e4e50f91b2fd96896d258b9c4bba7f611ca7b7ec9	f	2026-10-07 02:24:23.141344+05:30	2026-10-07 02:54:23.141344+05:30	2026-10-07 02:24:33.446266+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
605844a4-03e9-443c-ac66-96990f2520ee	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	40f412138871af056478af575a399f64e10d80b50fdd112f13dd82ad52af7738	f	2026-10-07 02:24:44.837085+05:30	2026-10-07 02:54:44.837085+05:30	2026-10-07 02:24:47.827591+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
45461d28-6eb2-45c9-830a-d6a26d4c82f9	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	5ba869d8fd6624e630056be5e15bea661724fbdace562cbf90fb0831f3b92fba	t	2026-10-10 01:24:28.951398+05:30	2026-10-10 01:54:28.951398+05:30	\N	\N	\N	\N
fa4917b7-82c8-4600-97b3-fefa6ad20f43	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	f1f297385169d12dd2d9d0ff124c92e16c3a4fb6779cfc2ca567dcb643db268d	t	2026-10-10 01:25:37.13063+05:30	2026-10-10 01:55:37.13063+05:30	\N	\N	\N	\N
ad016f1c-c8dd-4200-8ad7-ab46f47d7407	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	7a98241d7438dedbbd1235aba19bbfec403d54f417d165b1cdc90a3e81bac790	t	2026-10-10 01:25:37.163941+05:30	2026-10-10 01:55:37.163941+05:30	\N	\N	\N	\N
cb05017c-bd33-4bad-bf42-9bf5fd725fc2	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	21eefc049ecaaccd320ea5a515614cf9e2b9abc11c56e2489c1457bbe46be3bc	t	2026-10-10 01:25:37.169227+05:30	2026-10-10 01:55:37.169227+05:30	\N	\N	\N	\N
2808d885-6cb7-468e-bfcf-a46cd73193e7	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	d7b67d1f77156611394bc51336854c98f9ec05c42cc83dbff2394559504e4264	t	2026-10-10 01:25:37.178802+05:30	2026-10-10 01:55:37.178802+05:30	\N	\N	\N	\N
30f4e33c-8516-47fa-a312-3f1a1f2ad752	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	89c5d2a01ab404dd27e1681df83930c589af2501fc4b1e477faf936bad263814	t	2026-10-10 01:25:37.183048+05:30	2026-10-10 01:55:37.183048+05:30	\N	\N	\N	\N
70448258-ce21-4e5b-b1d6-253e3a432748	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	fd2ac9d351289d7332b45f6867d78071a351b1925d4470ae7d6d462029bb1355	t	2026-10-10 01:25:37.188136+05:30	2026-10-10 01:55:37.188136+05:30	\N	\N	\N	\N
71699d3e-b8e3-4f81-a0e2-a2eba8ef4338	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	52361eff8c39e5c1a8abed8472fc3cf97448de0b36e2d1f131f59f67434456d1	t	2026-10-10 01:25:37.194813+05:30	2026-10-10 01:55:37.194813+05:30	\N	\N	\N	\N
d4172bb9-d02e-46e1-84e9-b0f5f69c5a57	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	3ecc277b7f58059dc42443ee137dd7ea0fc5d58b37e630c74f37aeb37daaa650	f	2026-10-10 01:25:07.225374+05:30	2026-10-10 01:55:07.225374+05:30	2026-10-10 01:25:40.59729+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
87e72aec-5ad1-476a-bd71-46f8aa192055	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	508ca7879fc708cfca1697eb68e4b2dcfd47efb73ed711aa69e2479013cea8b0	f	2026-10-10 01:26:00.367265+05:30	2026-10-10 01:56:00.367265+05:30	2026-10-10 01:26:16.089723+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
0a7fcf9a-d7c8-4d06-83fe-5a5ae357686a	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	579d8d8c7e5aa80c1534da485636db071b4cfd77b78dcb6bc28cb1bc3559ab02	f	2026-10-10 01:28:36.244012+05:30	2026-10-10 01:58:36.244012+05:30	2026-10-10 01:28:40.89817+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
4bde06d8-eba8-4e38-9a36-0fbf3d8c5047	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	930c6b491bae6d52544c20410938e3d62ec812f93d393604feb3393931ccd56d	f	2026-10-10 01:28:55.090196+05:30	2026-10-10 01:58:55.090196+05:30	2026-10-10 01:29:31.057602+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
99a2afe7-8383-4771-8127-e3dc62700622	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0b92efac180794413d6ce9d2a0ad486d844a92bc5104e70ac3ce38be9ab8bf32	f	2026-10-10 01:29:37.473854+05:30	2026-10-10 01:59:37.473854+05:30	2026-10-10 01:29:56.372696+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
d75bbaa1-39ec-4be5-9448-99383a90ea6d	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	5d9494f45acf3f4648c26921cc9a6b8dd96b4fcc9d15e50c268dfe81c3b6ac1b	f	2026-10-10 01:33:26.998581+05:30	2026-10-10 02:03:26.998581+05:30	2026-10-10 01:33:43.926488+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
8d483284-9042-41d9-ab2d-7cd33de7b6c7	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	ff2d7fa4e8bc890535b025e95ef89d1ff281c48c98479c122df4b68c7561f356	f	2026-10-10 01:34:13.633383+05:30	2026-10-10 02:04:13.633383+05:30	2026-10-10 01:34:28.830545+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
f42bf964-bb3f-479e-ab73-50e2ac0ff470	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	dccc8059555adcfc9838361511881e58643b8a7a16c9b7ab9a5f8e21152ff2ba	f	2026-10-10 01:34:31.888815+05:30	2026-10-10 02:04:31.888815+05:30	2026-10-10 01:35:51.572378+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
4594f41f-6b51-4b48-ba9d-8ee15f3f4cd4	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	6dc00734f656587b6a676ad358a7fe397b82c6d3007ea154300fc80bb508a741	f	2026-10-10 01:50:04.07851+05:30	2026-10-10 02:20:04.07851+05:30	2026-10-10 01:50:17.169461+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
2dbc7195-1f27-444d-8f6c-8e4182fa68d6	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	0cc2191e69e8f515009a2a3614bd9deb0fb097287b087fad46997950512ba6ae	f	2026-10-10 01:50:26.475765+05:30	2026-10-10 02:20:26.475765+05:30	2026-10-10 01:50:39.584321+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
3e467eb0-f7ed-4b52-903c-3df32b9bcf49	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	c87ca320df81629d99898127e5c1871da52d5862d87819bdc9d37ed550be0f16	f	2026-10-10 01:50:54.264275+05:30	2026-10-10 02:20:54.264275+05:30	2026-10-10 01:51:19.34247+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
59966aae-45e3-4aa9-856a-76dbb59332a2	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	9cb0589dcb6e09b48be9cecd86e7bc58a4bbb8e9d7f3c7480e9ba9cf217562bc	f	2026-10-10 01:51:22.961208+05:30	2026-10-10 02:21:22.961208+05:30	2026-10-10 01:51:28.682019+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
c22ac9e4-03bd-42cb-95ae-2e6372f45def	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	6da7837b8d584e42c7602ec0ca1af633e6ea00f60dd9f7226e4a4b45902c5d0e	f	2026-10-10 01:51:31.760121+05:30	2026-10-10 02:21:31.760121+05:30	2026-10-10 01:53:33.753772+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
ccdc67e1-712b-477e-8848-440499d2139c	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	bac423c795461e169813f1f9218fe843858b27e5fcfb508910479c98f82d9fbd	f	2026-10-10 01:59:02.921048+05:30	2026-10-10 02:29:02.921048+05:30	2026-10-10 01:59:13.304693+05:30	SWITCH_IMPERSONATION	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
fee7382e-64bd-4e89-809f-55e49a3e614b	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	2efe4e298f9165476256760847f2d8758f59d8600d2161608d6356a40f67383c	f	2026-10-10 01:59:13.310591+05:30	2026-10-10 02:29:13.310591+05:30	2026-10-10 01:59:29.990855+05:30	SWITCH_IMPERSONATION	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
78492e57-fbce-4695-98ad-e9f0a09158e2	de526836-5e73-49d7-9be3-8ad07caa6090	0438f197-65cc-4fb2-8667-bdaceee1db81	11efd8f9e1a87f8d8af74239381e6638f9d9495c7ed5defc0555d6958a7ef5bf	f	2026-10-10 01:59:29.998019+05:30	2026-10-10 02:29:29.998019+05:30	2026-10-10 01:59:47.786292+05:30	SWITCH_IMPERSONATION	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
e6b548f1-fb83-4cd5-98c7-f7b78f197d09	de526836-5e73-49d7-9be3-8ad07caa6090	4ce61bc1-113e-42e4-a934-c58c9d61e541	f09513a3bc9a7f2d50ff358566fe714dd3aac977eae8c9eeef93130249152883	f	2026-10-10 01:59:47.812868+05:30	2026-10-10 02:29:47.812868+05:30	2026-10-10 02:00:01.050429+05:30	SWITCH_IMPERSONATION	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
bb47893b-2e7f-4e0f-a655-70fb2a828a24	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	b0a42157b64d2cee30dbc2e02c02060d80b63a7a9538db3d123dec0f63d57757	f	2026-10-10 02:00:01.053579+05:30	2026-10-10 02:30:01.053579+05:30	2026-10-10 02:00:12.672974+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
85fa0aaa-e571-4954-ace6-5ff5de1ada1a	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	3257882a64906454d2243814d47732edd9e6c32658169673dede32ccd1da1d42	f	2026-10-10 02:39:40.476337+05:30	2026-10-10 03:09:40.476337+05:30	2026-10-10 02:39:59.745704+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
7122bb84-41f1-4f5e-8458-76827c082ca0	de526836-5e73-49d7-9be3-8ad07caa6090	8554d145-bdd4-4ee6-b821-74b73cfe40bf	ca832996bcf875b6a79590b8f7ce5751d66c14df452a2e4886d079420f7add0c	f	2026-10-10 02:40:11.120458+05:30	2026-10-10 03:10:11.120458+05:30	2026-10-10 02:40:49.98121+05:30	LOGOUT	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
24af7cbb-89c4-45e8-a785-0fb08c78c038	de526836-5e73-49d7-9be3-8ad07caa6090	8554d145-bdd4-4ee6-b821-74b73cfe40bf	e1b5841c7386b29a350c160a7467d94d99c1bdc1eb79273126831c89a086499c	f	2026-10-10 02:41:20.026809+05:30	2026-10-10 03:11:20.026809+05:30	2026-10-10 02:42:43.113685+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
fad7a542-53e5-41f1-9902-c72ec3d13d2e	de526836-5e73-49d7-9be3-8ad07caa6090	8554d145-bdd4-4ee6-b821-74b73cfe40bf	b65064e0572af6edd53d49f6f339e56ab5ee5f19b8e19f57caf11814e4b5a096	f	2026-10-10 02:43:41.58195+05:30	2026-10-10 03:13:41.58195+05:30	2026-10-10 02:45:00.650043+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
72fb2382-ac9c-405f-92af-093d0045eb8f	de526836-5e73-49d7-9be3-8ad07caa6090	65b43201-4875-4caa-a601-b0b535019b48	ec1b8358d841cbedfba3d769f148c96414cfe4f3f5b4badbbcd00b95025fea9d	f	2026-10-10 02:47:20.999117+05:30	2026-10-10 03:17:20.999117+05:30	2026-10-10 02:47:48.943231+05:30	LOGOUT	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
fb07934b-effa-411e-bc0b-812218e0c23e	de526836-5e73-49d7-9be3-8ad07caa6090	65b43201-4875-4caa-a601-b0b535019b48	8db753e2498606788d5bbf9bc76a9f56cd3652c5720b4b159d28babcc3a0cd0f	f	2026-10-10 02:48:37.159734+05:30	2026-10-10 03:18:37.159734+05:30	2026-10-10 02:49:16.607938+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
5d0d1561-100f-4ce0-b3ef-e50c9f69757a	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	3867236b48110b7150f902e59ab716a1f623d7d43166ad43e00f1a1836dd3f68	f	2026-10-10 02:49:41.137891+05:30	2026-10-10 03:19:41.137891+05:30	2026-10-10 02:51:40.808383+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
50ff37c0-33f0-4e0c-a182-3878951d2a43	de526836-5e73-49d7-9be3-8ad07caa6090	65b43201-4875-4caa-a601-b0b535019b48	d4e58117c68489eb4d6730d217e4000b48863e99e8f95c4d652cb873cf226c17	f	2026-10-10 02:51:58.696461+05:30	2026-10-10 03:21:58.696461+05:30	2026-10-10 02:53:48.241741+05:30	RETURN_TO_ADMIN	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36
\.


--
-- Data for Name: module_master; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.module_master (module_id, module_code, module_name, parent_module_id, route, description, display_order, is_navigation, status, created_at, updated_at) FROM stdin;
58e433d2-4ef4-5e8c-97ef-14b4ea161c00	ADMIN	Admin	\N	/admin	Administrative settings, company management, and access controls	10	t	ACTIVE	2026-09-20 19:46:38.767473+05:30	2026-09-20 19:46:38.767473+05:30
7bcabdee-d53e-5e40-8856-6f40fa5311f3	SALES	Sales	\N	/sales	Sales pipeline, lead management, and customer conversions	20	t	ACTIVE	2026-09-20 19:46:38.767473+05:30	2026-09-20 19:46:38.767473+05:30
52c75db6-dd49-599c-9d77-6ff9754dfc48	OPERATIONS	Operations	\N	/operations	Client compliance workflows, task execution, and delivery	30	t	ACTIVE	2026-09-20 19:46:38.767473+05:30	2026-09-20 19:46:38.767473+05:30
15984459-38bc-5557-9eb5-ace2fa47e3ab	ADMIN_COMPANIES	Companies	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	/admin/companies	Corporate entities and company code prefixes	10	t	ACTIVE	2026-09-20 19:46:38.767473+05:30	2026-09-20 19:46:38.767473+05:30
41c4500a-3674-5bf4-8af2-bf448d16146d	ADMIN_DEPARTMENTS	Departments	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	/admin/departments	Company-specific department configuration	20	t	ACTIVE	2026-09-20 19:46:38.767473+05:30	2026-09-20 19:46:38.767473+05:30
869264e8-2cfa-572d-b81c-2a292a4e996b	ADMIN_DESIGNATIONS	Designations	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	/admin/designations	Company-specific employee designations and seniority ranks	30	t	ACTIVE	2026-09-20 19:46:38.767473+05:30	2026-09-20 19:46:38.767473+05:30
10b7bad6-1d95-5592-baa0-6e4fcbefa35f	ADMIN_EMPLOYEES	Employees	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	/admin/employees	Employee master records and organizational hierarchy	40	t	ACTIVE	2026-09-20 19:46:38.767473+05:30	2026-09-20 19:46:38.767473+05:30
fb6844ad-c156-5899-b55e-c55b99e3c81d	ADMIN_ACCESS	Access Control	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	/admin/access	User module permissions and role authorization	50	t	ACTIVE	2026-09-20 19:46:38.767473+05:30	2026-09-20 19:46:38.767473+05:30
e8f9e9e9-1017-5b99-adb7-e655f580e389	SALES_DASHBOARD	Sales Dashboard	7bcabdee-d53e-5e40-8856-6f40fa5311f3	/sales/dashboard	Sales overview and performance metrics	10	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
b7487e39-c3e8-57a2-a5e6-634c985b3c83	SALES_CONFIRMED_ORDER	Create Confirmed Order	7bcabdee-d53e-5e40-8856-6f40fa5311f3	/sales/confirmed-order	Create new confirmed sales orders	20	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
e70ce939-97de-5e44-b115-b41fa6d47363	SALES_MY_ORDERS	My Sales Orders	7bcabdee-d53e-5e40-8856-6f40fa5311f3	/sales/my-orders	View and manage sales orders created by current employee	30	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
d2ceb235-eb43-5ddb-9a49-b54af44240e0	SALES_ALL_ORDERS	All Sales Orders	7bcabdee-d53e-5e40-8856-6f40fa5311f3	/sales/all-orders	View and manage all sales orders within data scope	40	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
3329b014-3cd7-5a33-b75e-948b15c56214	SALES_CLIENT_MASTER	Client Master	7bcabdee-d53e-5e40-8856-6f40fa5311f3	/sales/clients	Manage corporate clients and accounts	50	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
f42007df-0de6-5461-9c79-98e63bf52adb	SALES_REPORTS	Sales Reports	7bcabdee-d53e-5e40-8856-6f40fa5311f3	/sales/reports	Sales performance and conversion reports	60	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
f9435bbf-e040-5269-9fe0-5e32b8e2b13b	OPERATION_DASHBOARD	Operation Dashboard	52c75db6-dd49-599c-9d77-6ff9754dfc48	/operations/dashboard	Operations workflow status and metrics	10	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
71bffc3c-37bb-57f7-b975-1da25326cbcb	OPERATION_UNASSIGNED_ORDERS	Unassigned Orders	52c75db6-dd49-599c-9d77-6ff9754dfc48	/operations/unassigned-orders	View and assign unassigned compliance orders	20	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
f11ebb42-4525-5cea-8f79-13eee46218eb	OPERATION_TASK_ASSIGNMENT	Task Assignment	52c75db6-dd49-599c-9d77-6ff9754dfc48	/operations/task-assignment	Assign and reassign compliance tasks across team	30	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
8ffea6ea-ffd6-5ad7-b660-2df3251af322	OPERATION_MY_TASKS	My Assigned Tasks	52c75db6-dd49-599c-9d77-6ff9754dfc48	/operations/my-tasks	Compliance tasks assigned to current employee	40	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
94302e7c-5d07-5fe3-87d6-0abbddd54017	OPERATION_ALL_TASKS	All Operation Tasks	52c75db6-dd49-599c-9d77-6ff9754dfc48	/operations/all-tasks	All compliance tasks within data scope	50	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
1b93187c-a974-50d1-a88f-e06395b01275	OPERATION_DOCUMENTS	Required Documents	52c75db6-dd49-599c-9d77-6ff9754dfc48	/operations/documents	Manage statutory compliance documents and checklists	60	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
030bc1e3-dc38-5a1f-a821-16cba85210d7	OPERATION_APPLICATION_STATUS	Application Status	52c75db6-dd49-599c-9d77-6ff9754dfc48	/operations/application-status	Track statutory filing and application statuses	70	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
856c9fc2-7524-579b-8142-d9f21fb3681f	OPERATION_REPORTS	Operation Reports	52c75db6-dd49-599c-9d77-6ff9754dfc48	/operations/reports	Operations turnaround time and completion reports	80	t	ACTIVE	2026-09-21 23:57:58.52938+05:30	2026-09-21 23:57:58.52938+05:30
dc80c923-8a29-5793-95de-70b3cd46fcad	ACCOUNTS	Accounts	\N	/accounts	Financial accounting, payments, invoicing, expenses, and ledgers	25	t	ACTIVE	2026-10-01 01:04:44.345831+05:30	2026-10-01 01:04:44.345831+05:30
4f96f9ef-2722-5327-b54a-638b195dc78d	ACCOUNTS_DASHBOARD	Accounts Dashboard	dc80c923-8a29-5793-95de-70b3cd46fcad	/accounts/dashboard	Financial overview, collections KPIs, and executive summaries	10	t	ACTIVE	2026-10-01 01:04:44.345831+05:30	2026-10-01 01:04:44.345831+05:30
78a60b47-6f1b-5b57-9f3f-5ed2699fe304	ACCOUNTS_PAYMENT_REGISTER	Payment Register	dc80c923-8a29-5793-95de-70b3cd46fcad	/accounts/payments	Record, verify, and track client payments and collections	20	t	ACTIVE	2026-10-01 01:04:44.345831+05:30	2026-10-01 01:04:44.345831+05:30
3cd0da8a-3cab-5ef6-9a32-d9a9d93e938c	ACCOUNTS_OUTSTANDING	Outstanding & Follow-ups	dc80c923-8a29-5793-95de-70b3cd46fcad	/accounts/outstanding	Debtor ageing, overdue receivables, and follow-up logging	30	t	ACTIVE	2026-10-01 01:04:44.345831+05:30	2026-10-01 01:04:44.345831+05:30
18e769eb-7e9c-53a6-b755-dff18784c20e	ACCOUNTS_INVOICES	Invoices & Receipts	dc80c923-8a29-5793-95de-70b3cd46fcad	/accounts/invoices	Manage Proforma invoices, Tax invoices, and document attachments	40	t	ACTIVE	2026-10-01 01:04:44.345831+05:30	2026-10-01 01:04:44.345831+05:30
1a151a5c-447f-53a0-b60e-ee8dfb30a74e	ACCOUNTS_EXPENSES	Expenses & Reimbursements	dc80c923-8a29-5793-95de-70b3cd46fcad	/accounts/expenses	Order direct costs, government fees, and employee reimbursement claims	50	t	ACTIVE	2026-10-01 01:04:44.345831+05:30	2026-10-01 01:04:44.345831+05:30
c486b814-f422-51a6-ab3b-a28667353323	ACCOUNTS_REPORTS	Accounts Reports	dc80c923-8a29-5793-95de-70b3cd46fcad	/accounts/reports	Financial ledgers, collections statements, and CSV exports	60	t	ACTIVE	2026-10-01 01:04:44.345831+05:30	2026-10-01 01:04:44.345831+05:30
c1cf3c01-2902-5d9d-b824-7514a43b7e04	ACCOUNTS_ENTRIES	Accounts Entries	dc80c923-8a29-5793-95de-70b3cd46fcad	/accounts/entries	Accounts entries ledger, invoicing, reimbursement notes, and remarks	20	t	ACTIVE	2026-10-10 00:24:34.356397+05:30	2026-10-10 00:24:34.356397+05:30
ffb8d9dd-e029-5d89-a423-f0c0dee70949	ADMIN_LICENSES	License Master	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	/admin/licenses	Statutory licenses and service catalog configuration	60	t	ACTIVE	2026-10-10 01:11:58.724382+05:30	2026-10-10 01:11:58.724382+05:30
\.


--
-- Data for Name: operation_application; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.operation_application (application_id, application_number, sales_order_id, company_id, client_id, service_id, assigned_to_user_id, assigned_by_user_id, assigned_at, priority, application_status, target_due_date, completion_date, assignment_notes, created_at, updated_at, deleted_at, deleted_by, deletion_reason) FROM stdin;
4ea8e868-36ad-4bf1-8faa-6ab242e954bd	AP-2026-0003	4b8fbf7e-35bf-420c-a022-9db4436abe34	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	40b5a081-65fb-5e83-819f-fa4a49c7977f	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-29 00:37:37.287516+05:30	MEDIUM	CANCELLED	2026-10-10	\N	\N	2026-09-24 02:53:59.175861+05:30	2026-10-31 12:06:20.914963+05:30	2026-10-31 12:06:20.914963+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	dummy entry
3997d4d2-bfb5-4a06-8cec-929270aeb419	AP-2026-0004	d028df71-155b-41e6-84ce-f7619697c96b	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	3fedfba5-e644-5643-9283-061b36dbf36c	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-24 03:23:14.086219+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-09-24 02:54:54.6905+05:30	2026-10-31 12:06:31.54437+05:30	2026-10-31 12:06:31.54437+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	dummy entry
db093cfd-6c3b-473c-ae66-9b295924aa36	AP-2026-0008	3a42eeeb-172d-486b-ad8a-98d6b647a46e	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	e0a8e4b8-3750-54ba-be0b-fa21906d8697	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-28 15:56:08.916015+05:30	MEDIUM	CANCELLED	2026-10-17	\N	urgent	2026-09-28 15:55:03.197591+05:30	2026-10-31 12:07:01.349678+05:30	2026-10-31 12:07:01.349678+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
058b6bc8-9285-43fd-8c52-67532eb40ac6	AP-2026-0009	2de435d8-b74d-4d31-95f3-2d4a37701ac9	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	79ba81bc-3247-59a3-9896-ce9766c46600	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-28 15:57:17.640968+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-09-28 15:57:17.610013+05:30	2026-10-31 12:07:21.439531+05:30	2026-10-31 12:07:21.439531+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
e0a66aa9-91bf-4214-85e2-5d8e270f2b23	AP-2026-0010	027b8d57-fce7-4f60-ae50-a8ccd7cb5e03	5242338c-3887-56db-b86c-c59deae26654	4973250a-e81d-4c05-8f20-93c83e86c635	3fedfba5-e644-5643-9283-061b36dbf36c	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-28 15:58:28.217222+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-09-28 15:58:28.190352+05:30	2026-10-31 12:07:26.169987+05:30	2026-10-31 12:07:26.169987+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	AP-2026-0011	c7c8d7f1-26f9-46d7-ac24-0ba21db409eb	5242338c-3887-56db-b86c-c59deae26654	8d2cae66-0949-4781-9c3c-4a501aba928c	e0a8e4b8-3750-54ba-be0b-fa21906d8697	0438f197-65cc-4fb2-8667-bdaceee1db81	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-29 16:54:24.198527+05:30	MEDIUM	APPROVED	2026-10-22	2026-09-29	\N	2026-09-29 16:53:39.808136+05:30	2026-10-31 12:07:34.927719+05:30	2026-10-31 12:07:34.927719+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	dummy entry
543de9f0-dcb8-47b4-b98f-5b194e1258f3	AP-2026-0012	7c0282ad-764c-41f0-950c-00d0db5b8464	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	e1ad76a3-a315-4c76-b64e-77cbc7b9a6d9	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-30 10:47:10.179705+05:30	MEDIUM	CANCELLED	2026-10-23	\N	\N	2026-09-30 10:46:29.540439+05:30	2026-10-31 12:07:38.988466+05:30	2026-10-31 12:07:38.988466+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
f25069b3-5013-4ebb-82ef-cea01267657c	AP-2026-0035	be4a1a11-c14b-40cf-9032-835e278465d2	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	3fedfba5-e644-5643-9283-061b36dbf36c	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-26 00:08:10.155718+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-26 (Ref: Sl No 1.0)	2026-10-26 00:08:10.110917+05:30	2026-10-31 12:07:42.118273+05:30	2026-10-31 12:07:42.118273+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
e32bf79c-e6e2-4615-b1f2-8040247c3f18	AP-2026-0022	216eccee-dfbb-48f0-8a63-217ba2b167eb	5242338c-3887-56db-b86c-c59deae26654	a11df6a4-62e1-4193-9943-fc6940fc3cc5	e1ad76a3-a315-4c76-b64e-77cbc7b9a6d9	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-24 22:59:12.869192+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-10-24 22:59:12.837226+05:30	2026-10-31 12:07:52.658268+05:30	2026-10-31 12:07:52.658268+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
a939e2c4-35b9-47c9-9f8a-bc448c5bb877	AP-2026-0021	ce006ca7-42c0-4b87-85bc-bd92fe729ffb	5242338c-3887-56db-b86c-c59deae26654	a11df6a4-62e1-4193-9943-fc6940fc3cc5	c7adcc88-0569-57e1-af74-a85737bdc641	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-24 22:56:52.756781+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-10-24 22:56:52.733047+05:30	2026-10-31 12:07:56.549579+05:30	2026-10-31 12:07:56.549579+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
4adf326f-6dda-4684-ab74-874667a59a0b	AP-2026-0020	a8c86af8-353e-45ad-be11-10187e517cf7	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	c7adcc88-0569-57e1-af74-a85737bdc641	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-24 22:55:03.214409+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-10-24 22:55:03.17085+05:30	2026-10-31 12:07:59.544928+05:30	2026-10-31 12:07:59.544928+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
9b78f07f-d6c0-41ce-a08e-a255e0426fe9	AP-2026-0019	78f5dcf1-214e-4075-8501-fb05af2d7bd8	46deca34-710f-5c79-83ab-939b03bffa22	683e7249-ea02-409f-bdc5-fca7a8a7e415	55e21cf3-8fca-4241-b8c9-1f5699520d12	0438f197-65cc-4fb2-8667-bdaceee1db81	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 18:23:56.579824+05:30	MEDIUM	APPROVED	2026-10-24	2026-10-10	chalo bhaiilog kaam aagya hai	2026-10-10 02:44:56.415556+05:30	2026-10-31 12:08:09.740188+05:30	2026-10-31 12:08:09.740188+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	Dummy entry
da56b220-e470-4487-a407-48645b60dbdc	AP-2026-0018	a408e780-d55a-4137-a4a2-b8a90bd1bc29	5242338c-3887-56db-b86c-c59deae26654	a11df6a4-62e1-4193-9943-fc6940fc3cc5	c7adcc88-0569-57e1-af74-a85737bdc641	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-09 19:27:56.248847+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-10-09 19:27:56.209419+05:30	2026-10-31 12:08:13.643257+05:30	2026-10-31 12:08:13.643257+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
bbbc717f-d53c-4475-a7ea-9ff5066ab79a	AP-2026-0017	ce897913-8de9-422d-8d1f-f415cf3504a7	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	e1ad76a3-a315-4c76-b64e-77cbc7b9a6d9	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-09 19:21:57.479945+05:30	MEDIUM	CANCELLED	2026-10-17	\N	\N	2026-10-09 19:03:35.633475+05:30	2026-10-31 12:08:16.495194+05:30	2026-10-31 12:08:16.495194+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
b5fdb615-3dba-4a07-bcc8-ebcd273928f0	AP-2026-0016	c3f09177-7fc9-436b-bdd5-d177c419d38e	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	e1ad76a3-a315-4c76-b64e-77cbc7b9a6d9	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-07 16:20:18.561035+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-10-07 16:08:17.554545+05:30	2026-10-31 12:08:18.874935+05:30	2026-10-31 12:08:18.874935+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
dece3eea-3f5b-46f5-9d7c-29ad9334097c	AP-2026-0015	7558b3f8-00f9-4897-a5b2-5d01f137555c	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	e0a8e4b8-3750-54ba-be0b-fa21906d8697	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-07 01:33:59.349217+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-10-07 01:33:59.33512+05:30	2026-10-31 12:08:21.379945+05:30	2026-10-31 12:08:21.379945+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	AP-2026-0013	9f937f0a-66bf-4635-ba53-739203287a4c	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	c7adcc88-0569-57e1-af74-a85737bdc641	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-30 11:16:20.224252+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-09-30 11:16:20.182113+05:30	2026-10-31 12:08:28.590881+05:30	2026-10-31 12:08:28.590881+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
e78b8f08-be2e-4424-9799-6895e872e8c2	AP-2026-0005	a6b5ebfb-4a44-4dd6-acf7-d13a5bc6a9d5	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	b42c5d8d-2820-566b-bfad-26a329fc914f	\N	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	2026-09-25 11:12:33.009191+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-09-25 11:12:32.950864+05:30	2026-09-26 01:20:21.453539+05:30	\N	\N	\N
51d9ae10-f22d-448f-a560-c2a9323ffea8	AP-2026-0006	ee014d1f-6522-476e-ac87-0976bb52048a	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	c7adcc88-0569-57e1-af74-a85737bdc641	\N	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	2026-09-25 14:04:23.600944+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-09-25 14:04:23.568611+05:30	2026-09-26 01:26:05.937831+05:30	\N	\N	\N
e1770a62-2997-4d34-9258-9300d62d5cbf	AP-2026-0001	77b1df77-3aab-4394-b737-abc82994eb3a	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	c7adcc88-0569-57e1-af74-a85737bdc641	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-24 00:04:47.770945+05:30	MEDIUM	CANCELLED	2026-10-31	\N	twst2	2026-09-23 23:42:54.314988+05:30	2026-10-19 12:31:24.253476+05:30	\N	\N	\N
bf7aa794-c1d2-452e-b6d3-ba838dd10b02	AP-2026-0025	36311f50-9a3c-4203-a79f-6b59eb66a8dc	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	55e21cf3-8fca-4241-b8c9-1f5699520d12	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-25 22:19:21.689015+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-25 (Ref: Sl No 3.0)	2026-10-25 22:19:21.553027+05:30	2026-10-25 23:01:44.739141+05:30	2026-10-25 23:01:44.739141+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
eaeea2ed-76f7-4b5a-a5be-a9f304b72275	AP-2026-0027	3b514f9b-87f3-410d-b475-da6c8d41d9f7	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	b42c5d8d-2820-566b-bfad-26a329fc914f	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-25 22:19:21.750756+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-25 (Ref: Sl No 5.0)	2026-10-25 22:19:21.553027+05:30	2026-10-25 23:01:48.002443+05:30	2026-10-25 23:01:48.002443+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
2f3b7575-2066-493a-a62c-fc95be74d0fb	AP-2026-0026	1f859330-e63f-40f4-ba79-abf2d3714b28	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	a22e7dcd-6495-5311-883c-93fc61c87ef4	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-25 22:19:21.717474+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-25 (Ref: Sl No 4.0)	2026-10-25 22:19:21.553027+05:30	2026-10-25 23:01:58.070864+05:30	2026-10-25 23:01:58.070864+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
950cc940-dbb1-45e3-a4fc-276eced83899	AP-2026-0024	249e834e-1cd7-45b5-8707-f78e0ccea2a3	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	79ba81bc-3247-59a3-9896-ce9766c46600	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-25 22:19:21.671225+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-25 (Ref: Sl No 2.0)	2026-10-25 22:19:21.553027+05:30	2026-10-25 23:02:05.343881+05:30	2026-10-25 23:02:05.343881+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
8553d61d-cce7-4877-8474-9a990c4ee4ec	AP-2026-0023	b7dc6d32-f9ea-4222-adf2-f68aa48f16f1	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	3fedfba5-e644-5643-9283-061b36dbf36c	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-25 22:19:21.606159+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-25 (Ref: Sl No 1.0)	2026-10-25 22:19:21.553027+05:30	2026-10-25 23:02:09.213476+05:30	2026-10-25 23:02:09.213476+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
2df25880-1b91-4ed4-9eb4-9aa54cb56f53	AP-2026-0034	e50488bf-3e95-449e-ac02-2af61871b164	5242338c-3887-56db-b86c-c59deae26654	a11df6a4-62e1-4193-9943-fc6940fc3cc5	3fedfba5-e644-5643-9283-061b36dbf36c	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-25 23:48:24.484026+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-10-25 23:48:24.453326+05:30	2026-10-25 23:52:16.203462+05:30	2026-10-25 23:52:16.203462+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
2bed4f2b-61f3-45b0-bf20-474a212be9e3	AP-2026-0033	4af7b6bf-3ff9-41b8-bb28-5cbc588eb07f	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	3fedfba5-e644-5643-9283-061b36dbf36c	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-25 23:37:35.86555+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-25 (Ref: Sl No 5.0)	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:52:19.692351+05:30	2026-10-25 23:52:19.692351+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
71ae120b-7250-43d3-a092-ca60b8366bfa	AP-2026-0031	082cc2aa-0177-42ae-b670-03e815776e28	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	55e21cf3-8fca-4241-b8c9-1f5699520d12	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-25 23:37:35.822343+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-25 (Ref: Sl No 3.0)	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:52:22.243153+05:30	2026-10-25 23:52:22.243153+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
ca0c550f-6f0e-4b06-8466-66fc8b221831	AP-2026-0029	df7f3086-b111-4174-97a6-3f0d5966a2c3	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	3fedfba5-e644-5643-9283-061b36dbf36c	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-25 23:37:35.760523+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-25 (Ref: Sl No 1.0)	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:52:24.971144+05:30	2026-10-25 23:52:24.971144+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
733b35e2-4330-4588-aa1f-5ec8d6df279c	AP-2026-0030	98c27bf9-6ba5-4db2-a536-842ed7aad7e4	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	79ba81bc-3247-59a3-9896-ce9766c46600	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-25 23:37:35.803022+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-25 (Ref: Sl No 2.0)	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:52:27.691696+05:30	2026-10-25 23:52:27.691696+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
5975e799-fb23-4f30-8f31-4338ed37ee4a	AP-2026-0032	c70382c1-9155-480c-b725-a4a10ba56020	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	a22e7dcd-6495-5311-883c-93fc61c87ef4	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-25 23:37:35.841892+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-25 (Ref: Sl No 4.0)	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:52:29.732426+05:30	2026-10-25 23:52:29.732426+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
680e84cc-4054-49d2-b147-d6a86b5b9a13	AP-2026-0028	c59e5da3-5272-46c4-8f1f-7810b7647c8c	5242338c-3887-56db-b86c-c59deae26654	a11df6a4-62e1-4193-9943-fc6940fc3cc5	3fedfba5-e644-5643-9283-061b36dbf36c	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-25 23:04:54.405026+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-10-25 23:04:54.377324+05:30	2026-10-25 23:52:37.604036+05:30	2026-10-25 23:52:37.604036+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
e5837191-599a-4c9d-ac0d-58f9e442045c	AP-2026-0037	d2fee853-0b72-4c9f-94eb-09c7022a2364	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	55e21cf3-8fca-4241-b8c9-1f5699520d12	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-26 00:08:10.226672+05:30	MEDIUM	APPROVED	\N	2026-10-26	Bulk imported on 2026-10-26 (Ref: Sl No 3.0)	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:38:04.067502+05:30	2026-10-26 00:38:04.067502+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	giugiu
3ca55838-d953-4175-a37a-780ff438c869	AP-2026-0002	280da9e2-783d-4bbe-bde3-d30755a0eac6	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	547b955f-8d2e-5abd-9151-4c33ae212cf4	0438f197-65cc-4fb2-8667-bdaceee1db81	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	2026-09-24 02:25:05.275544+05:30	MEDIUM	APPROVED	2026-10-30	2026-09-25	test entery\n	2026-09-24 00:04:08.416007+05:30	2026-10-31 12:06:12.829026+05:30	2026-10-31 12:06:12.829026+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	dummy entry
6bccf11d-68fe-4020-bac4-820936578bec	AP-2026-0007	b237ea09-b7b5-401f-8b12-e00a530a525c	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	e0a8e4b8-3750-54ba-be0b-fa21906d8697	0438f197-65cc-4fb2-8667-bdaceee1db81	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	2026-09-25 14:06:46.200601+05:30	MEDIUM	APPROVED	2026-09-30	2026-09-25	\N	2026-09-25 14:06:06.490372+05:30	2026-10-31 12:07:16.834664+05:30	2026-10-31 12:07:16.834664+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	dummy entry
38ce8f41-9a04-40d2-acc8-543390e99cbf	AP-2026-0039	3580eeaa-4a41-478a-b9bf-750d201462ba	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	e1ad76a3-a315-4c76-b64e-77cbc7b9a6d9	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-26 00:08:10.276566+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-26 (Ref: Sl No 5.0)	2026-10-26 00:08:10.110917+05:30	2026-10-31 12:07:44.815731+05:30	2026-10-31 12:07:44.815731+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
f05bb899-190f-40b0-b993-038e3011bf0b	AP-2026-0038	990fefe7-5e97-43d2-a8fb-071848f09bc2	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	a22e7dcd-6495-5311-883c-93fc61c87ef4	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-26 00:08:10.249106+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-26 (Ref: Sl No 4.0)	2026-10-26 00:08:10.110917+05:30	2026-10-31 12:07:47.483113+05:30	2026-10-31 12:07:47.483113+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
68bae788-12d3-40a8-97be-06ec36f8772e	AP-2026-0036	49573950-2950-4bd2-9b3f-8b0b72781f51	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	79ba81bc-3247-59a3-9896-ce9766c46600	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-26 00:08:10.204686+05:30	MEDIUM	CANCELLED	\N	\N	Bulk imported on 2026-10-26 (Ref: Sl No 2.0)	2026-10-26 00:08:10.110917+05:30	2026-10-31 12:07:50.067049+05:30	2026-10-31 12:07:50.067049+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
0eef383e-ac4b-4541-a9a7-e0b98de5d548	AP-2026-0014	e78da1c9-8d92-4e76-bc36-700770eecaab	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	c7adcc88-0569-57e1-af74-a85737bdc641	\N	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-07 01:33:04.45794+05:30	MEDIUM	CANCELLED	\N	\N	\N	2026-10-07 01:33:04.422815+05:30	2026-10-31 12:08:23.87694+05:30	2026-10-31 12:08:23.87694+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
4196c2a9-282c-40ee-8a75-2aebc5eef45d	AP-2026-0041	654e9028-c1d1-43eb-bdb8-d2f8e36a0f31	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	3fedfba5-e644-5643-9283-061b36dbf36c	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	de526836-5e73-49d7-9be3-8ad07caa6090	2026-11-01 18:42:14.777592+05:30	MEDIUM	ASSIGNED	\N	\N	Bulk imported on 2026-11-01 (Ref: Sl No 1.0)	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30	\N	\N	\N
3f2029b1-d446-46d9-960e-5ee9e676dd71	AP-2026-0042	4acc34dd-67f3-4afa-945f-134a4fa396fa	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	79ba81bc-3247-59a3-9896-ce9766c46600	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	de526836-5e73-49d7-9be3-8ad07caa6090	2026-11-01 18:42:14.810223+05:30	MEDIUM	ASSIGNED	\N	\N	Bulk imported on 2026-11-01 (Ref: Sl No 2.0)	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30	\N	\N	\N
7f96f52b-ecc5-4172-a5e6-7018ebb135d7	AP-2026-0043	ec94c66a-343d-44b8-a8a5-c864ee8947c1	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	3fedfba5-e644-5643-9283-061b36dbf36c	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	de526836-5e73-49d7-9be3-8ad07caa6090	2026-11-01 18:42:14.834967+05:30	MEDIUM	ASSIGNED	\N	\N	Bulk imported on 2026-11-01 (Ref: Sl No 3.0)	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30	\N	\N	\N
68d5f2f9-a3a6-469c-b790-6ff2f5da8529	AP-2026-0044	3bedc686-8f48-45f1-b760-fbe97941f44c	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	a22e7dcd-6495-5311-883c-93fc61c87ef4	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	de526836-5e73-49d7-9be3-8ad07caa6090	2026-11-01 18:42:14.855958+05:30	MEDIUM	ASSIGNED	\N	\N	Bulk imported on 2026-11-01 (Ref: Sl No 4.0)	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30	\N	\N	\N
342cb97c-953e-4643-bd89-7a2bd88ec2e8	AP-2026-0045	266c12f0-57ad-40ea-a62e-6c199c2e5290	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	55e21cf3-8fca-4241-b8c9-1f5699520d12	65b43201-4875-4caa-a601-b0b535019b48	de526836-5e73-49d7-9be3-8ad07caa6090	2026-11-02 18:36:14.450267+05:30	MEDIUM	ASSIGNED	2026-11-24	\N	Bulk imported on 2026-11-01 (Ref: Sl No 5.0)	2026-11-01 18:42:14.74885+05:30	2026-11-02 18:36:14.419242+05:30	\N	\N	\N
7b2791ff-c6bc-4ebe-9dbc-bec76ce3bdd5	AP-2026-0040	e4862b88-2c44-4601-8233-f8afcdd5497d	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	3fedfba5-e644-5643-9283-061b36dbf36c	0438f197-65cc-4fb2-8667-bdaceee1db81	de526836-5e73-49d7-9be3-8ad07caa6090	2026-11-02 18:36:38.2648+05:30	MEDIUM	ASSIGNED	2026-11-30	\N	\N	2026-11-01 18:41:07.525029+05:30	2026-11-02 18:36:38.248338+05:30	\N	\N	\N
\.


--
-- Data for Name: operation_remark; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.operation_remark (remark_id, application_id, author_user_id, remark_text, created_at) FROM stdin;
f7e5788b-d1d6-4345-a4e0-08e6133e529e	6bccf11d-68fe-4020-bac4-820936578bec	0438f197-65cc-4fb2-8667-bdaceee1db81	delay ho raha hai bhaii	2026-09-26 01:57:57.173187+05:30
1b497c5b-fec4-4244-b10b-efc116c27519	6bccf11d-68fe-4020-bac4-820936578bec	0438f197-65cc-4fb2-8667-bdaceee1db81	are bhaii bhaii	2026-09-26 02:14:02.775174+05:30
a2eac044-07ae-4c03-8cf4-c78782e5575d	3ca55838-d953-4175-a37a-780ff438c869	0438f197-65cc-4fb2-8667-bdaceee1db81	NOT POSSIBLE	2026-09-28 16:02:14.873895+05:30
23298b22-0eef-43c0-a043-81353079a384	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	DHFGBLH	2026-09-29 16:57:03.827507+05:30
3826e54f-0fa8-4fdb-a9da-76f39b6d7d8c	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	de526836-5e73-49d7-9be3-8ad07caa6090	GFDGFD,UF	2026-09-29 17:00:45.74438+05:30
634e6813-7191-425b-9b40-b92c09e52d61	543de9f0-dcb8-47b4-b98f-5b194e1258f3	0438f197-65cc-4fb2-8667-bdaceee1db81	jckthdctluvj	2026-09-30 10:49:18.104984+05:30
7a127d28-c594-4b13-89a0-65e257d4e1ee	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	hello start the conversation	2026-10-08 23:54:50.534083+05:30
29a8bbe1-5629-441c-b538-4ea022392687	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	hello secound conversation	2026-10-08 23:55:18.48581+05:30
162790c3-9202-4067-aec8-e6f0ac56f1dd	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	last conversation	2026-10-08 23:55:43.270509+05:30
b44c2681-8c8e-4a0c-a52f-f24b88760173	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	0438f197-65cc-4fb2-8667-bdaceee1db81	hello testing	2026-10-09 00:01:05.271678+05:30
cf38c4fa-a67c-41c5-b752-1a881b3eaf23	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	0438f197-65cc-4fb2-8667-bdaceee1db81	kya bhaii sucessfull ho gya kya	2026-10-09 00:36:13.554952+05:30
c5ad0600-9d77-4d32-a20b-de5b4c2f68c6	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	haa siir	2026-10-09 00:36:26.799785+05:30
383cc7c7-ce55-493d-a1c3-1f382daf31b4	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	hello gyus	2026-10-09 00:37:41.385078+05:30
25447ff1-a4da-4abc-89ae-96b42e017bb1	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	kya bhaii moj kr di lala heheh	2026-10-09 01:04:16.537733+05:30
ce92ad61-22ed-4ae1-81ee-9284eb5af1fb	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	or bhaiiiii aa gya swaad	2026-10-09 13:39:28.465619+05:30
c2ec43f4-4a8e-429e-ac36-a5e9f80aa65a	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	de526836-5e73-49d7-9be3-8ad07caa6090	heheh haaji	2026-10-09 13:54:56.270212+05:30
0a59cdca-f0c2-47dd-93c5-e6336e388485	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	ky hai	2026-10-09 13:55:11.209514+05:30
c8972a1f-15fc-4649-a946-ef7a381d628a	0eef383e-ac4b-4541-a9a7-e0b98de5d548	de526836-5e73-49d7-9be3-8ad07caa6090	next to next	2026-10-09 13:55:32.769987+05:30
f9b2d9b2-162d-4d87-9864-44ba7c40d64f	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	hb ygv	2026-10-09 19:19:26.029788+05:30
81153465-082f-4eca-b161-1a09462b4b3e	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	de526836-5e73-49d7-9be3-8ad07caa6090	CALL AKASH 456789	2026-10-09 19:34:33.962955+05:30
5388f548-b082-4152-a95e-14a046424cad	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	65b43201-4875-4caa-a601-b0b535019b48	site naii chal rahahia	2026-10-10 02:52:52.429684+05:30
62cbf2f9-67cd-48d5-9bbb-21dc960dc38a	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	65b43201-4875-4caa-a601-b0b535019b48	done mera kaam ho gy ahai	2026-10-10 02:53:42.079597+05:30
3d88ab37-a120-432f-8081-3b033fe83ae2	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	0438f197-65cc-4fb2-8667-bdaceee1db81	haa ji paaji	2026-10-10 14:29:45.170322+05:30
\.


--
-- Data for Name: operations_coordinator_config; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.operations_coordinator_config (config_id, company_id, coordinator_user_id, updated_by_user_id, created_at, updated_at) FROM stdin;
7ca69bfe-32bc-43bd-993c-af8de9f1d3ef	46deca34-710f-5c79-83ab-939b03bffa22	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	2026-10-09 01:07:14.187018+05:30	2026-10-09 01:07:14.187018+05:30
3267d65d-5240-4f0e-96f7-91b1b5d30e85	5242338c-3887-56db-b86c-c59deae26654	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	\N	2026-10-09 01:07:14.187018+05:30	2026-10-09 01:07:14.187018+05:30
\.


--
-- Data for Name: payment_transaction; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.payment_transaction (payment_id, company_id, sales_order_id, payment_number, amount, payment_date, payment_mode, transaction_reference, receiving_account, proof_attachment_path, proof_attachment_name, remark, submitted_by_user_id, submitted_at, verification_status, verified_by_user_id, verified_at, reversal_reason, reversed_by_user_id, reversed_at, is_opening_balance, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: permission_audit_log; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.permission_audit_log (audit_id, actor_user_id, target_user_id, action_type, before_state, after_state, ip_address, user_agent, created_at) FROM stdin;
d163799b-472b-44d8-a647-3c2adf96e4a1	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	PERMISSION_UPDATE	{"is_hod": false, "user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "is_active": true, "last_name": "Singhal", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Mansi", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Muskan Gupta", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "CG0003", "designation_id": "df74d857-6fc7-5dc9-b085-667b5eed5e43", "official_email": "hr@gocompliances.com", "department_name": "Operations", "manager_user_id": "69984504-68fe-470a-9240-4a37edf511b8", "designation_name": "Manager", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "is_active": true, "last_name": "Singhal", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Mansi", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Muskan Gupta", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "CG0003", "designation_id": "df74d857-6fc7-5dc9-b085-667b5eed5e43", "official_email": "hr@gocompliances.com", "department_name": "Operations", "manager_user_id": "69984504-68fe-470a-9240-4a37edf511b8", "designation_name": "Manager", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	2026-09-22 01:13:42.12397+05:30
66dce74d-a49e-4b25-a070-1b9d45578dd8	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	PERMISSION_UPDATE	{"is_hod": false, "user_id": "fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b", "is_active": true, "last_name": "Upadhyay", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Karishma", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "2326fd8f-44f5-5b3f-8fbd-d11942c8404e", "employee_code": "CG0004", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "xyz@gmail.com", "department_name": "Sales", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b", "is_active": true, "last_name": "Upadhyay", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Karishma", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "2326fd8f-44f5-5b3f-8fbd-d11942c8404e", "employee_code": "CG0004", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "xyz@gmail.com", "department_name": "Sales", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	2026-09-22 01:14:12.279937+05:30
b53ae7ce-5469-4b6e-9395-e6d20fe9c14f	de526836-5e73-49d7-9be3-8ad07caa6090	0438f197-65cc-4fb2-8667-bdaceee1db81	PERMISSION_UPDATE	{"is_hod": false, "user_id": "0438f197-65cc-4fb2-8667-bdaceee1db81", "is_active": true, "last_name": "Kumar", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Deepak", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "CG0005", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "projectsgocompliances@gmail.com", "department_name": "Operations", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "0438f197-65cc-4fb2-8667-bdaceee1db81", "is_active": true, "last_name": "Kumar", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Deepak", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "CG0005", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "projectsgocompliances@gmail.com", "department_name": "Operations", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	2026-09-22 11:29:59.25451+05:30
a29ba693-307c-4125-8cfe-5bb7949b43c0	de526836-5e73-49d7-9be3-8ad07caa6090	de526836-5e73-49d7-9be3-8ad07caa6090	PERMISSION_UPDATE	{"is_hod": false, "user_id": "de526836-5e73-49d7-9be3-8ad07caa6090", "is_active": true, "last_name": "Admin", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Super", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Muskan Gupta", "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "CG0001", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "research.rnd.gc@gmail.com", "department_name": "Administration", "manager_user_id": "69984504-68fe-470a-9240-4a37edf511b8", "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "de526836-5e73-49d7-9be3-8ad07caa6090", "is_active": true, "last_name": "Admin", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Super", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Muskan Gupta", "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "CG0001", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "research.rnd.gc@gmail.com", "department_name": "Administration", "manager_user_id": "69984504-68fe-470a-9240-4a37edf511b8", "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	103.171.172.132	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	2026-09-23 01:46:57.682563+05:30
e97f7307-6eba-45e8-bca4-cefa957736d5	de526836-5e73-49d7-9be3-8ad07caa6090	de526836-5e73-49d7-9be3-8ad07caa6090	PERMISSION_UPDATE	{"is_hod": false, "user_id": "de526836-5e73-49d7-9be3-8ad07caa6090", "is_active": true, "last_name": "Admin", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Super", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Muskan Gupta", "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "CG0001", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "research.rnd.gc@gmail.com", "department_name": "Administration", "manager_user_id": "69984504-68fe-470a-9240-4a37edf511b8", "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "de526836-5e73-49d7-9be3-8ad07caa6090", "is_active": true, "last_name": "Admin", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Super", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Muskan Gupta", "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "CG0001", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "research.rnd.gc@gmail.com", "department_name": "Administration", "manager_user_id": "69984504-68fe-470a-9240-4a37edf511b8", "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	103.171.172.132	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	2026-09-23 01:54:56.64425+05:30
c9f6c14e-76c9-4d7b-8e35-3afe9f809dd5	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	PERMISSION_UPDATE	{"is_hod": false, "user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "is_active": true, "last_name": "Singhal", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Mansi", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Muskan Gupta", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "CG0003", "designation_id": "df74d857-6fc7-5dc9-b085-667b5eed5e43", "official_email": "hr@gocompliances.com", "department_name": "Operations", "manager_user_id": "69984504-68fe-470a-9240-4a37edf511b8", "designation_name": "Manager", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "is_active": true, "last_name": "Singhal", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Mansi", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Muskan Gupta", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "CG0003", "designation_id": "df74d857-6fc7-5dc9-b085-667b5eed5e43", "official_email": "hr@gocompliances.com", "department_name": "Operations", "manager_user_id": "69984504-68fe-470a-9240-4a37edf511b8", "designation_name": "Manager", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	2026-09-23 16:22:46.140044+05:30
367988d5-4b90-44f4-8192-6c15d85b1eed	de526836-5e73-49d7-9be3-8ad07caa6090	0438f197-65cc-4fb2-8667-bdaceee1db81	PERMISSION_UPDATE	{"is_hod": false, "user_id": "0438f197-65cc-4fb2-8667-bdaceee1db81", "is_active": true, "last_name": "Kumar", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Deepak", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "CG0005", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "projectsgocompliances@gmail.com", "department_name": "Operations", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "0438f197-65cc-4fb2-8667-bdaceee1db81", "is_active": true, "last_name": "Kumar", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Deepak", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "CG0005", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "projectsgocompliances@gmail.com", "department_name": "Operations", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	2026-09-24 00:12:02.041622+05:30
5533ebf4-c352-48f0-9048-fa9daca41292	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	PERMISSION_UPDATE	{"is_hod": false, "user_id": "fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b", "is_active": true, "last_name": "Upadhyay", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Karishma", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "2326fd8f-44f5-5b3f-8fbd-d11942c8404e", "employee_code": "CG0004", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "xyz@gmail.com", "department_name": "Sales", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b", "is_active": true, "last_name": "Upadhyay", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Karishma", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "2326fd8f-44f5-5b3f-8fbd-d11942c8404e", "employee_code": "CG0004", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "xyz@gmail.com", "department_name": "Sales", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	2026-09-24 02:48:14.347045+05:30
d8fc9ce6-38dc-4ab3-92c7-ab0608d3f37b	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	PERMISSION_UPDATE	{"is_hod": false, "user_id": "fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b", "is_active": true, "last_name": "Upadhyay", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Karishma", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "2326fd8f-44f5-5b3f-8fbd-d11942c8404e", "employee_code": "CG0004", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "xyz@gmail.com", "department_name": "Sales", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b", "is_active": true, "last_name": "Upadhyay", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Karishma", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "2326fd8f-44f5-5b3f-8fbd-d11942c8404e", "employee_code": "CG0004", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "xyz@gmail.com", "department_name": "Sales", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	2026-09-24 02:48:51.232854+05:30
93a4341b-09fd-456a-a587-ffd420c52ff0	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	PERMISSION_UPDATE	{"is_hod": false, "user_id": "fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b", "is_active": true, "last_name": "Upadhyay", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Karishma", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "2326fd8f-44f5-5b3f-8fbd-d11942c8404e", "employee_code": "CG0004", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "xyz@gmail.com", "department_name": "Sales", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b", "is_active": true, "last_name": "Upadhyay", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Karishma", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "2326fd8f-44f5-5b3f-8fbd-d11942c8404e", "employee_code": "CG0004", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "xyz@gmail.com", "department_name": "Sales", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36	2026-09-24 02:51:10.529936+05:30
835322da-d219-44c9-a810-e2b401da2e8f	de526836-5e73-49d7-9be3-8ad07caa6090	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	PERMISSION_UPDATE	{"is_hod": false, "user_id": "fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b", "is_active": true, "last_name": "Upadhyay", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Karishma", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "2326fd8f-44f5-5b3f-8fbd-d11942c8404e", "employee_code": "CG0004", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "xyz@gmail.com", "department_name": "Sales", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b", "is_active": true, "last_name": "Upadhyay", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Karishma", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "2326fd8f-44f5-5b3f-8fbd-d11942c8404e", "employee_code": "CG0004", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "xyz@gmail.com", "department_name": "Sales", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-09-25 11:09:21.345694+05:30
d635a83b-d8b8-4296-9aa4-de61d5773dbc	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	PERMISSION_UPDATE	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "CG0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "CG0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	\N	\N	2026-10-10 00:25:15.456133+05:30
6fe3eac4-227d-4149-a009-aafceb5faeb7	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	PERMISSION_UPDATE	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "CG0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "CG0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	python-httpx/0.28.1	2026-10-10 00:25:25.816694+05:30
0f09cf82-ed00-4171-a5ce-64dd88a37810	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	PERMISSION_UPDATE	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "CG0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "CG0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 00:34:52.266657+05:30
b746afee-58f0-4e19-a854-bed13d488040	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	PERMISSION_UPDATE	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "GC0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "GC0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	\N	\N	2026-10-10 01:17:11.362826+05:30
541754ab-4241-41f2-8cda-feaa68d82328	de526836-5e73-49d7-9be3-8ad07caa6090	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	PERMISSION_UPDATE	{"is_hod": false, "user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "is_active": true, "last_name": "Singhal", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Mansi", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Muskan Gupta", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "GC0003", "designation_id": "df74d857-6fc7-5dc9-b085-667b5eed5e43", "official_email": "hr@gocompliances.com", "department_name": "Operations", "manager_user_id": "69984504-68fe-470a-9240-4a37edf511b8", "designation_name": "Manager", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "is_active": true, "last_name": "Singhal", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Mansi", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Muskan Gupta", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "GC0003", "designation_id": "df74d857-6fc7-5dc9-b085-667b5eed5e43", "official_email": "hr@gocompliances.com", "department_name": "Operations", "manager_user_id": "69984504-68fe-470a-9240-4a37edf511b8", "designation_name": "Manager", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 01:34:06.437002+05:30
f19822cd-b025-44f2-834f-4d31f0b28716	de526836-5e73-49d7-9be3-8ad07caa6090	8554d145-bdd4-4ee6-b821-74b73cfe40bf	PERMISSION_UPDATE	{"is_hod": false, "user_id": "8554d145-bdd4-4ee6-b821-74b73cfe40bf", "is_active": true, "last_name": "Soni", "company_id": "46deca34-710f-5c79-83ab-939b03bffa22", "first_name": "Reeya", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Enterpernership", "manager_name": null, "department_id": "2326fd8f-44f5-5b3f-8fbd-d11942c8404e", "employee_code": "EP0001", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "ab@gmail.com", "department_name": "Sales", "manager_user_id": null, "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "8554d145-bdd4-4ee6-b821-74b73cfe40bf", "is_active": true, "last_name": "Soni", "company_id": "46deca34-710f-5c79-83ab-939b03bffa22", "first_name": "Reeya", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Enterpernership", "manager_name": null, "department_id": "2326fd8f-44f5-5b3f-8fbd-d11942c8404e", "employee_code": "EP0001", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "ab@gmail.com", "department_name": "Sales", "manager_user_id": null, "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:39:20.352723+05:30
475171b6-e6b0-4c91-8a51-a8b4461dd0d9	de526836-5e73-49d7-9be3-8ad07caa6090	65b43201-4875-4caa-a601-b0b535019b48	PERMISSION_UPDATE	{"is_hod": false, "user_id": "65b43201-4875-4caa-a601-b0b535019b48", "is_active": true, "last_name": "Choudhary", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Hrithik", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "GC0008", "designation_id": "b15c7681-9eb7-5751-a553-82dcd245b163", "official_email": "abc@gmail.com", "department_name": "Operations", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Executive", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "65b43201-4875-4caa-a601-b0b535019b48", "is_active": true, "last_name": "Choudhary", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Hrithik", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "GC0008", "designation_id": "b15c7681-9eb7-5751-a553-82dcd245b163", "official_email": "abc@gmail.com", "department_name": "Operations", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Executive", "primary_location": null, "is_reporting_manager": false}	127.0.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36	2026-10-10 02:46:57.684835+05:30
7867fbde-f55a-4d3a-bdd0-ab7aefa98e1d	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	PERMISSION_UPDATE	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "GC0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "GC0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	\N	\N	2026-10-13 13:00:02.597447+05:30
5a5cdf9e-9cde-43de-86d4-2b80bdef0858	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	PERMISSION_COPY	{"target_before": {"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": true, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": true}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "GC0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}, "source_user_id": "de526836-5e73-49d7-9be3-8ad07caa6090"}	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "GC0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	\N	\N	2026-10-13 13:00:02.685066+05:30
45de59fb-62f9-4d1e-8834-952f17b81e4b	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	PERMISSION_UPDATE	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "GC0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "GC0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	\N	\N	2026-10-13 13:13:14.482313+05:30
31429f29-4fe5-4444-9375-03aafee2c22a	de526836-5e73-49d7-9be3-8ad07caa6090	69984504-68fe-470a-9240-4a37edf511b8	PERMISSION_COPY	{"target_before": {"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "GC0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}, "source_user_id": "de526836-5e73-49d7-9be3-8ad07caa6090"}	{"is_hod": false, "user_id": "69984504-68fe-470a-9240-4a37edf511b8", "is_active": true, "last_name": "Gupta", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Muskan", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": true, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": true, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "ALL", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": true, "can_delete": true, "can_export": false, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "a9593c21-af68-5071-9436-ee1f58930c3e", "employee_code": "GC0002", "designation_id": "91482014-6f86-54a6-beeb-cce2557dc001", "official_email": "gocompliances@gmail.com", "department_name": "Administration", "manager_user_id": null, "designation_name": "Director", "primary_location": null, "is_reporting_manager": false}	\N	\N	2026-10-13 13:13:14.542115+05:30
f7b4625f-395e-4a38-a22b-48da31352c1c	de526836-5e73-49d7-9be3-8ad07caa6090	dcdee779-494b-4fe7-afa1-d3b66c784fbb	PERMISSION_UPDATE	{"is_hod": false, "user_id": "dcdee779-494b-4fe7-afa1-d3b66c784fbb", "is_active": true, "last_name": "Kumar", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Abhishek", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "GC0007", "designation_id": "08dff813-b33d-5afc-88f8-a90ae8ee77d4", "official_email": "mahtoabhi07@gmail.com", "department_name": "Operations", "manager_user_id": null, "designation_name": "Assistant Manager", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "dcdee779-494b-4fe7-afa1-d3b66c784fbb", "is_active": true, "last_name": "Kumar", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Abhishek", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": true, "can_view": true, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "COMPANY", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": null, "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "GC0007", "designation_id": "08dff813-b33d-5afc-88f8-a90ae8ee77d4", "official_email": "mahtoabhi07@gmail.com", "department_name": "Operations", "manager_user_id": null, "designation_name": "Assistant Manager", "primary_location": null, "is_reporting_manager": false}	\N	\N	2026-10-13 13:37:10.40464+05:30
dcae9ea7-8a44-4462-90f9-31cd3589caca	69984504-68fe-470a-9240-4a37edf511b8	0438f197-65cc-4fb2-8667-bdaceee1db81	PERMISSION_UPDATE	{"is_hod": false, "user_id": "0438f197-65cc-4fb2-8667-bdaceee1db81", "is_active": true, "last_name": "Kumar", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Deepak", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": true, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "GC0005", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "projectsgocompliances@gmail.com", "department_name": "Operations", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	{"is_hod": false, "user_id": "0438f197-65cc-4fb2-8667-bdaceee1db81", "is_active": true, "last_name": "Kumar", "company_id": "5242338c-3887-56db-b86c-c59deae26654", "first_name": "Deepak", "permissions": [{"status": "ACTIVE", "can_edit": false, "can_view": true, "page_code": "SALES_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CONFIRMED_ORDER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_MY_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_ALL_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_CLIENT_MASTER", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "SALES_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_UNASSIGNED_ORDERS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_TASK_ASSIGNMENT", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_MY_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_ALL_TASKS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_DOCUMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_APPLICATION_STATUS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "OPERATION_REPORTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_DASHBOARD", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ACCOUNTS_ENTRIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_EMPLOYEES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_ACCESS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_COMPANIES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DEPARTMENTS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_DESIGNATIONS", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}, {"status": "ACTIVE", "can_edit": false, "can_view": false, "page_code": "ADMIN_LICENSES", "can_assign": false, "can_create": false, "can_delete": false, "can_export": false, "data_scope": "SELF", "can_approve": false, "can_reassign": false}], "company_name": "Gocompliances", "manager_name": "Mansi Singhal", "department_id": "996d9e8f-777e-5a29-a2fb-6feebbce6c1b", "employee_code": "GC0005", "designation_id": "2477adb3-666c-55d9-81e8-1f925f729d5e", "official_email": "projectsgocompliances@gmail.com", "department_name": "Operations", "manager_user_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "designation_name": "Senior Executive", "primary_location": null, "is_reporting_manager": false}	\N	\N	2026-10-14 15:52:20.655607+05:30
\.


--
-- Data for Name: sales_order; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.sales_order (order_id, order_number, company_id, client_id, service_id, salesperson_user_id, lead_source, order_date, order_value, amount_received, balance_amount, payment_status, confirmation_status, confirmed_at, notes, created_at, updated_at, proforma_invoice_no, tax_invoice_no, reimbursement_note, govt_fees, incidental_cost, profit_amount, location, gst_invoice_required, deleted_at, deleted_by, deletion_reason) FROM stdin;
280da9e2-783d-4bbe-bde3-d30755a0eac6	SO-2026-0002	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	547b955f-8d2e-5abd-9151-4c33ae212cf4	de526836-5e73-49d7-9be3-8ad07caa6090	REFERRAL	2026-09-23	11000.00	5000.00	6000.00	PARTIALLY_PAID	CANCELLED	2026-09-24 00:04:08.43377+05:30	\N	2026-09-24 00:03:15.627241+05:30	2026-10-31 12:06:12.829026+05:30	\N	\N	\N	500.00	1000.00	9500.00	\N	f	2026-10-31 12:06:12.829026+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	dummy entry
4b8fbf7e-35bf-420c-a022-9db4436abe34	SO-2026-0003	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	40b5a081-65fb-5e83-819f-fa4a49c7977f	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	WEBSITE	2026-09-23	15000.00	500.00	14500.00	PARTIALLY_PAID	CANCELLED	2026-09-24 02:53:59.214801+05:30	\N	2026-09-24 02:53:59.175861+05:30	2026-10-31 12:06:20.914963+05:30	\N	\N	\N	2500.00	0.00	12500.00	\N	f	2026-10-31 12:06:20.914963+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	dummy entry
d028df71-155b-41e6-84ce-f7619697c96b	SO-2026-0004	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	3fedfba5-e644-5643-9283-061b36dbf36c	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	REFERRAL	2026-09-23	25000.00	567.00	24433.00	PARTIALLY_PAID	CANCELLED	2026-09-24 02:54:54.722026+05:30	\N	2026-09-24 02:54:54.6905+05:30	2026-10-31 12:06:31.54437+05:30	\N	\N	\N	5000.00	0.00	20000.00	\N	f	2026-10-31 12:06:31.54437+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	dummy entry
3a42eeeb-172d-486b-ad8a-98d6b647a46e	SO-2026-0008	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	e0a8e4b8-3750-54ba-be0b-fa21906d8697	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	REFERRAL	2026-09-28	50000.00	2000.00	48000.00	PARTIALLY_PAID	CANCELLED	2026-09-28 15:55:03.236226+05:30	\N	2026-09-28 15:55:03.197591+05:30	2026-10-31 12:07:01.349678+05:30	\N	\N	\N	5000.00	2000.00	43000.00	\N	f	2026-10-31 12:07:01.349678+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
b237ea09-b7b5-401f-8b12-e00a530a525c	SO-2026-0007	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	e0a8e4b8-3750-54ba-be0b-fa21906d8697	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	JUSTDIAL	2026-09-25	500000.00	500000.00	0.00	FULLY_PAID	CANCELLED	2026-09-25 14:06:06.511792+05:30	\N	2026-09-25 14:06:06.490372+05:30	2026-10-31 12:07:16.834664+05:30	\N	\N	\N	25000.00	100000.00	375000.00	\N	f	2026-10-31 12:07:16.834664+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	dummy entry
2de435d8-b74d-4d31-95f3-2d4a37701ac9	SO-2026-0009	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	79ba81bc-3247-59a3-9896-ce9766c46600	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	WEBSITE	2026-09-28	5000.00	2000.00	3000.00	PARTIALLY_PAID	CANCELLED	2026-09-28 15:57:17.640968+05:30	\N	2026-09-28 15:57:17.610013+05:30	2026-10-31 12:07:21.439531+05:30	\N	\N	\N	500.00	2000.00	2500.00	\N	f	2026-10-31 12:07:21.439531+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
027b8d57-fce7-4f60-ae50-a8ccd7cb5e03	SO-2026-0010	5242338c-3887-56db-b86c-c59deae26654	4973250a-e81d-4c05-8f20-93c83e86c635	3fedfba5-e644-5643-9283-061b36dbf36c	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	WEBSITE	2026-09-28	20000.00	2000.00	18000.00	PARTIALLY_PAID	CANCELLED	2026-09-28 15:58:28.217222+05:30	\N	2026-09-28 15:58:28.190352+05:30	2026-10-31 12:07:26.169987+05:30	\N	\N	\N	5000.00	2000.00	13000.00	\N	f	2026-10-31 12:07:26.169987+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
c7c8d7f1-26f9-46d7-ac24-0ba21db409eb	SO-2026-0011	5242338c-3887-56db-b86c-c59deae26654	8d2cae66-0949-4781-9c3c-4a501aba928c	e0a8e4b8-3750-54ba-be0b-fa21906d8697	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	REFERRAL	2026-09-29	500000.00	25000.00	475000.00	PARTIALLY_PAID	CANCELLED	2026-09-29 16:53:39.847958+05:30	\N	2026-09-29 16:53:39.808136+05:30	2026-10-31 12:07:34.927719+05:30	\N	\N	\N	50000.00	100000.00	350000.00	\N	f	2026-10-31 12:07:34.927719+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	dummy entry
7c0282ad-764c-41f0-950c-00d0db5b8464	SO-2026-0012	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	e1ad76a3-a315-4c76-b64e-77cbc7b9a6d9	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	REFERRAL	2026-09-30	50000.00	5000.00	45000.00	PARTIALLY_PAID	CANCELLED	2026-09-30 10:46:29.5856+05:30	\N	2026-09-30 10:46:29.540439+05:30	2026-10-31 12:07:38.988466+05:30	\N	\N	\N	2000.00	1000.00	47000.00	\N	f	2026-10-31 12:07:38.988466+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
216eccee-dfbb-48f0-8a63-217ba2b167eb	SO-2026-0022	5242338c-3887-56db-b86c-c59deae26654	a11df6a4-62e1-4193-9943-fc6940fc3cc5	e1ad76a3-a315-4c76-b64e-77cbc7b9a6d9	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-24	11800.00	5000.00	6800.00	PARTIALLY_PAID	CANCELLED	2026-10-24 22:59:12.869192+05:30	\N	2026-10-24 22:59:12.837226+05:30	2026-10-31 12:07:52.658268+05:30	\N	\N	\N	5000.00	2000.00	4800.00	Sector 62, Noida, Uttar Pradesh, India	t	2026-10-31 12:07:52.658268+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
ce006ca7-42c0-4b87-85bc-bd92fe729ffb	SO-2026-0021	5242338c-3887-56db-b86c-c59deae26654	a11df6a4-62e1-4193-9943-fc6940fc3cc5	c7adcc88-0569-57e1-af74-a85737bdc641	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	WEBSITE	2026-10-24	11800.00	500.00	11300.00	PARTIALLY_PAID	CANCELLED	2026-10-24 22:56:52.756781+05:30	\N	2026-10-24 22:56:52.733047+05:30	2026-10-31 12:07:56.549579+05:30	\N	\N	\N	482.00	0.00	11318.00	Sector 62, Noida, Uttar Pradesh, India	t	2026-10-31 12:07:56.549579+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
a6b5ebfb-4a44-4dd6-acf7-d13a5bc6a9d5	SO-2026-0005	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	b42c5d8d-2820-566b-bfad-26a329fc914f	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	REFERRAL	2026-09-25	10000.00	0.00	10000.00	PENDING	CANCELLED	2026-09-25 11:12:33.009191+05:30	\N	2026-09-25 11:12:32.950864+05:30	2026-09-26 01:20:21.453517+05:30	\N	\N	\N	2000.00	0.00	8000.00	\N	f	\N	\N	\N
ee014d1f-6522-476e-ac87-0976bb52048a	SO-2026-0006	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	c7adcc88-0569-57e1-af74-a85737bdc641	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	WEBSITE	2026-09-25	15000.00	5000.00	10000.00	PARTIALLY_PAID	CANCELLED	2026-09-25 14:04:23.600944+05:30	\N	2026-09-25 14:04:23.568611+05:30	2026-09-26 01:26:05.937816+05:30	\N	\N	\N	1000.00	1000.00	13000.00	\N	f	\N	\N	\N
a8c86af8-353e-45ad-be11-10187e517cf7	SO-2026-0020	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	c7adcc88-0569-57e1-af74-a85737bdc641	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	WEBSITE	2026-10-24	1000.00	500.00	500.00	PARTIALLY_PAID	CANCELLED	2026-10-24 22:55:03.214409+05:30	\N	2026-10-24 22:55:03.17085+05:30	2026-10-31 12:07:59.544928+05:30	\N	\N	\N	50.00	0.00	950.00	Noida	f	2026-10-31 12:07:59.544928+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
78f5dcf1-214e-4075-8501-fb05af2d7bd8	SO-2026-0019	46deca34-710f-5c79-83ab-939b03bffa22	683e7249-ea02-409f-bdc5-fca7a8a7e415	55e21cf3-8fca-4241-b8c9-1f5699520d12	8554d145-bdd4-4ee6-b821-74b73cfe40bf	DIRECT	2026-10-09	100000.00	10000.00	90000.00	PARTIALLY_PAID	CANCELLED	2026-10-10 02:44:56.482069+05:30	done mera kaam ho gy ahai	2026-10-10 02:44:56.415556+05:30	2026-10-31 12:08:09.740188+05:30	\N	\N	\N	100.00	1.00	99899.00	Noida	t	2026-10-31 12:08:09.740188+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	Dummy entry
a408e780-d55a-4137-a4a2-b8a90bd1bc29	SO-2026-0018	5242338c-3887-56db-b86c-c59deae26654	a11df6a4-62e1-4193-9943-fc6940fc3cc5	c7adcc88-0569-57e1-af74-a85737bdc641	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	DIRECT	2026-10-09	1000000.00	1000.00	999000.00	PARTIALLY_PAID	CANCELLED	2026-10-09 19:27:56.248847+05:30	\N	2026-10-09 19:27:56.209419+05:30	2026-10-31 12:08:13.643257+05:30	\N	\N	\N	100.00	198.00	999702.00	Bangalore	f	2026-10-31 12:08:13.643257+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
ce897913-8de9-422d-8d1f-f415cf3504a7	SO-2026-0017	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	e1ad76a3-a315-4c76-b64e-77cbc7b9a6d9	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	JUSTDIAL	2026-10-09	100000.00	20000.00	80000.00	PARTIALLY_PAID	CANCELLED	2026-10-09 19:03:35.685795+05:30	CALL AKASH 456789	2026-10-09 19:03:35.633475+05:30	2026-10-31 12:08:16.495194+05:30	24562772	63782882	2672377823	500.00	20000.00	79500.00	Noida	t	2026-10-31 12:08:16.495194+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
c3f09177-7fc9-436b-bdd5-d177c419d38e	SO-2026-0016	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	e1ad76a3-a315-4c76-b64e-77cbc7b9a6d9	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	INDIAMART	2026-10-07	100000.00	20000.00	80000.00	PARTIALLY_PAID	CANCELLED	2026-10-07 16:08:17.601928+05:30	haa ji paaji	2026-10-07 16:08:17.554545+05:30	2026-10-31 12:08:18.874935+05:30	ybyugf6gt	vtcfr5	vftcvt	500.00	100.00	99400.00	Noida	t	2026-10-31 12:08:18.874935+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
7558b3f8-00f9-4897-a5b2-5d01f137555c	SO-2026-0015	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	e0a8e4b8-3750-54ba-be0b-fa21906d8697	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	WEBSITE	2026-10-06	1000000.00	1.00	999999.00	PARTIALLY_PAID	CANCELLED	2026-10-07 01:33:59.349217+05:30	hello guyss	2026-10-07 01:33:59.33512+05:30	2026-10-31 12:08:21.379945+05:30	\N	\N	\N	1.00	1.00	999998.00	Bangalore	t	2026-10-31 12:08:21.379945+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
e78da1c9-8d92-4e76-bc36-700770eecaab	SO-2026-0014	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	c7adcc88-0569-57e1-af74-a85737bdc641	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	DIRECT	2026-10-06	50000.00	12000.00	38000.00	PARTIALLY_PAID	CANCELLED	2026-10-07 01:33:04.45794+05:30	next to next	2026-10-07 01:33:04.422815+05:30	2026-10-31 12:08:23.87694+05:30	\N	\N	\N	500.00	10000.00	39500.00	Noida	f	2026-10-31 12:08:23.87694+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
9f937f0a-66bf-4635-ba53-739203287a4c	SO-2026-0013	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	c7adcc88-0569-57e1-af74-a85737bdc641	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	WEBSITE	2026-09-30	100000.00	20000.00	80000.00	PARTIALLY_PAID	CANCELLED	2026-09-30 11:16:20.224252+05:30	vdfb kjgfd	2026-09-30 11:16:20.182113+05:30	2026-10-31 12:08:28.590881+05:30	sfvklflvdmfvlkmd	dfm ,fd. dnlkdfn	df vnf mv	200.00	100.00	99700.00	Ambala	f	2026-10-31 12:08:28.590881+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
e4862b88-2c44-4601-8233-f8afcdd5497d	SO-2026-0040	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	3fedfba5-e644-5643-9283-061b36dbf36c	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	JUSTDIAL	2026-11-01	11800.00	1000.00	10800.00	PARTIALLY_PAID	CONFIRMED	2026-11-01 18:41:07.574263+05:30	\N	2026-11-01 18:41:07.525029+05:30	2026-11-01 18:41:07.525029+05:30	\N	\N	\N	0.00	0.00	11800.00	Noida	t	\N	\N	\N
77b1df77-3aab-4394-b737-abc82994eb3a	SO-2026-0001	5242338c-3887-56db-b86c-c59deae26654	db62ec41-a44c-47fa-8baf-218673960742	c7adcc88-0569-57e1-af74-a85737bdc641	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	WEBSITE	2026-09-23	35000.00	5000.00	30000.00	PARTIALLY_PAID	CANCELLED	2026-09-23 23:42:54.373144+05:30	VUYOU	2026-09-23 23:42:54.314988+05:30	2026-10-19 12:31:24.25346+05:30	GVCUU	KBIUBP	YCYTI	1000.00	17000.00	17000.00	\N	f	\N	\N	\N
36311f50-9a3c-4203-a79f-6b59eb66a8dc	SO-2026-0025	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	55e21cf3-8fca-4241-b8c9-1f5699520d12	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-25	30000.00	0.00	30000.00	PENDING	CANCELLED	2026-10-25 22:19:21.689015+05:30	Bulk imported on 2026-10-25 (Ref: Sl No 3.0)	2026-10-25 22:19:21.553027+05:30	2026-10-25 23:01:44.739141+05:30	\N	\N	\N	0.00	300.00	29700.00	Mumbai	f	2026-10-25 23:01:44.739141+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
1f859330-e63f-40f4-ba79-abf2d3714b28	SO-2026-0026	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	a22e7dcd-6495-5311-883c-93fc61c87ef4	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-25	40000.00	0.00	40000.00	PENDING	CANCELLED	2026-10-25 22:19:21.717474+05:30	Bulk imported on 2026-10-25 (Ref: Sl No 4.0)	2026-10-25 22:19:21.553027+05:30	2026-10-25 23:01:58.070864+05:30	\N	\N	\N	0.00	400.00	39600.00	jharkhand	f	2026-10-25 23:01:58.070864+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
249e834e-1cd7-45b5-8707-f78e0ccea2a3	SO-2026-0024	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	79ba81bc-3247-59a3-9896-ce9766c46600	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-25	20000.00	0.00	20000.00	PENDING	CANCELLED	2026-10-25 22:19:21.671225+05:30	Bulk imported on 2026-10-25 (Ref: Sl No 2.0)	2026-10-25 22:19:21.553027+05:30	2026-10-25 23:02:05.343881+05:30	\N	\N	\N	0.00	200.00	19800.00	delhi	f	2026-10-25 23:02:05.343881+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
b7dc6d32-f9ea-4222-adf2-f68aa48f16f1	SO-2026-0023	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	3fedfba5-e644-5643-9283-061b36dbf36c	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-25	10000.00	0.00	10000.00	PENDING	CANCELLED	2026-10-25 22:19:21.606159+05:30	Bulk imported on 2026-10-25 (Ref: Sl No 1.0)	2026-10-25 22:19:21.553027+05:30	2026-10-25 23:02:09.213476+05:30	\N	\N	\N	0.00	100.00	9900.00	Noida	f	2026-10-25 23:02:09.213476+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
d2fee853-0b72-4c9f-94eb-09c7022a2364	SO-2026-0037	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	55e21cf3-8fca-4241-b8c9-1f5699520d12	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-26	35400.00	500.00	34900.00	PARTIALLY_PAID	CANCELLED	2026-10-26 00:08:10.226672+05:30	Bulk imported on 2026-10-26 (Ref: Sl No 3.0)	2026-10-26 00:08:10.110917+05:30	2026-10-26 00:38:04.067502+05:30	\N	\N	\N	0.00	300.00	35100.00	Mumbai	t	2026-10-26 00:38:04.067502+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	giugiu
3b514f9b-87f3-410d-b475-da6c8d41d9f7	SO-2026-0027	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	b42c5d8d-2820-566b-bfad-26a329fc914f	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-25	50000.00	0.00	50000.00	PENDING	CANCELLED	2026-10-25 22:19:21.750756+05:30	Bulk imported on 2026-10-25 (Ref: Sl No 5.0)	2026-10-25 22:19:21.553027+05:30	2026-10-25 23:01:48.002443+05:30	\N	\N	\N	0.00	500.00	49500.00	jammu	f	2026-10-25 23:01:48.002443+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
be4a1a11-c14b-40cf-9032-835e278465d2	SO-2026-0035	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	3fedfba5-e644-5643-9283-061b36dbf36c	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-26	11800.00	500.00	11300.00	PARTIALLY_PAID	CANCELLED	2026-10-26 00:08:10.155718+05:30	Bulk imported on 2026-10-26 (Ref: Sl No 1.0)	2026-10-26 00:08:10.110917+05:30	2026-10-31 12:07:42.118273+05:30	\N	\N	\N	0.00	100.00	11700.00	Noida	t	2026-10-31 12:07:42.118273+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
3580eeaa-4a41-478a-b9bf-750d201462ba	SO-2026-0039	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	e1ad76a3-a315-4c76-b64e-77cbc7b9a6d9	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-26	59000.00	500.00	58500.00	PARTIALLY_PAID	CANCELLED	2026-10-26 00:08:10.276566+05:30	Bulk imported on 2026-10-26 (Ref: Sl No 5.0)	2026-10-26 00:08:10.110917+05:30	2026-10-31 12:07:44.815731+05:30	\N	\N	\N	0.00	500.00	58500.00	jammu	t	2026-10-31 12:07:44.815731+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
990fefe7-5e97-43d2-a8fb-071848f09bc2	SO-2026-0038	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	a22e7dcd-6495-5311-883c-93fc61c87ef4	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-26	47200.00	500.00	46700.00	PARTIALLY_PAID	CANCELLED	2026-10-26 00:08:10.249106+05:30	Bulk imported on 2026-10-26 (Ref: Sl No 4.0)	2026-10-26 00:08:10.110917+05:30	2026-10-31 12:07:47.483113+05:30	\N	\N	\N	0.00	400.00	46800.00	jharkhand	t	2026-10-31 12:07:47.483113+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
49573950-2950-4bd2-9b3f-8b0b72781f51	SO-2026-0036	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	79ba81bc-3247-59a3-9896-ce9766c46600	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-26	23600.00	500.00	23100.00	PARTIALLY_PAID	CANCELLED	2026-10-26 00:08:10.204686+05:30	Bulk imported on 2026-10-26 (Ref: Sl No 2.0)	2026-10-26 00:08:10.110917+05:30	2026-10-31 12:07:50.067049+05:30	\N	\N	\N	0.00	200.00	23400.00	delhi	t	2026-10-31 12:07:50.067049+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
654e9028-c1d1-43eb-bdb8-d2f8e36a0f31	SO-2026-0041	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	3fedfba5-e644-5643-9283-061b36dbf36c	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-11-01	10000.00	500.00	9500.00	PARTIALLY_PAID	CONFIRMED	2026-11-01 18:42:14.777592+05:30	Bulk imported on 2026-11-01 (Ref: Sl No 1.0)	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30	\N	\N	\N	0.00	100.00	9900.00	Noida	f	\N	\N	\N
4acc34dd-67f3-4afa-945f-134a4fa396fa	SO-2026-0042	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	79ba81bc-3247-59a3-9896-ce9766c46600	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-11-01	20000.00	500.00	19500.00	PARTIALLY_PAID	CONFIRMED	2026-11-01 18:42:14.810223+05:30	Bulk imported on 2026-11-01 (Ref: Sl No 2.0)	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30	\N	\N	\N	0.00	200.00	19800.00	delhi	f	\N	\N	\N
ec94c66a-343d-44b8-a8a5-c864ee8947c1	SO-2026-0043	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	3fedfba5-e644-5643-9283-061b36dbf36c	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-11-01	30000.00	500.00	29500.00	PARTIALLY_PAID	CONFIRMED	2026-11-01 18:42:14.834967+05:30	Bulk imported on 2026-11-01 (Ref: Sl No 3.0)	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30	\N	\N	\N	0.00	300.00	29700.00	Mumbai	f	\N	\N	\N
3bedc686-8f48-45f1-b760-fbe97941f44c	SO-2026-0044	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	a22e7dcd-6495-5311-883c-93fc61c87ef4	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-11-01	40000.00	500.00	39500.00	PARTIALLY_PAID	CONFIRMED	2026-11-01 18:42:14.855958+05:30	Bulk imported on 2026-11-01 (Ref: Sl No 4.0)	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30	\N	\N	\N	0.00	400.00	39600.00	jharkhand	f	\N	\N	\N
266c12f0-57ad-40ea-a62e-6c199c2e5290	SO-2026-0045	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	55e21cf3-8fca-4241-b8c9-1f5699520d12	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-11-01	50000.00	500.00	49500.00	PARTIALLY_PAID	CONFIRMED	2026-11-01 18:42:14.875774+05:30	Bulk imported on 2026-11-01 (Ref: Sl No 5.0)	2026-11-01 18:42:14.74885+05:30	2026-11-01 18:42:14.74885+05:30	\N	\N	\N	0.00	500.00	49500.00	jammu	f	\N	\N	\N
e50488bf-3e95-449e-ac02-2af61871b164	SO-2026-0034	5242338c-3887-56db-b86c-c59deae26654	a11df6a4-62e1-4193-9943-fc6940fc3cc5	3fedfba5-e644-5643-9283-061b36dbf36c	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	WEBSITE	2026-10-25	11800.00	100.00	11700.00	PARTIALLY_PAID	CANCELLED	2026-10-25 23:48:24.484026+05:30	\N	2026-10-25 23:48:24.453326+05:30	2026-10-25 23:52:16.203462+05:30	\N	\N	\N	100.00	100.00	11600.00	england	t	2026-10-25 23:52:16.203462+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
4af7b6bf-3ff9-41b8-bb28-5cbc588eb07f	SO-2026-0033	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	3fedfba5-e644-5643-9283-061b36dbf36c	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-25	50000.00	500.00	49500.00	PARTIALLY_PAID	CANCELLED	2026-10-25 23:37:35.86555+05:30	Bulk imported on 2026-10-25 (Ref: Sl No 5.0)	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:52:19.692351+05:30	\N	\N	\N	0.00	500.00	49500.00	jammu	f	2026-10-25 23:52:19.692351+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
082cc2aa-0177-42ae-b670-03e815776e28	SO-2026-0031	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	55e21cf3-8fca-4241-b8c9-1f5699520d12	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-25	30000.00	500.00	29500.00	PARTIALLY_PAID	CANCELLED	2026-10-25 23:37:35.822343+05:30	Bulk imported on 2026-10-25 (Ref: Sl No 3.0)	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:52:22.243153+05:30	\N	\N	\N	0.00	300.00	29700.00	Mumbai	f	2026-10-25 23:52:22.243153+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
df7f3086-b111-4174-97a6-3f0d5966a2c3	SO-2026-0029	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	3fedfba5-e644-5643-9283-061b36dbf36c	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-25	10000.00	500.00	9500.00	PARTIALLY_PAID	CANCELLED	2026-10-25 23:37:35.760523+05:30	Bulk imported on 2026-10-25 (Ref: Sl No 1.0)	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:52:24.971144+05:30	\N	\N	\N	0.00	100.00	9900.00	Noida	f	2026-10-25 23:52:24.971144+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
98c27bf9-6ba5-4db2-a536-842ed7aad7e4	SO-2026-0030	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	79ba81bc-3247-59a3-9896-ce9766c46600	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-25	20000.00	500.00	19500.00	PARTIALLY_PAID	CANCELLED	2026-10-25 23:37:35.803022+05:30	Bulk imported on 2026-10-25 (Ref: Sl No 2.0)	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:52:27.691696+05:30	\N	\N	\N	0.00	200.00	19800.00	delhi	f	2026-10-25 23:52:27.691696+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
c70382c1-9155-480c-b725-a4a10ba56020	SO-2026-0032	5242338c-3887-56db-b86c-c59deae26654	6b1e36ad-e64c-4a55-ad31-c5622c26bf85	a22e7dcd-6495-5311-883c-93fc61c87ef4	de526836-5e73-49d7-9be3-8ad07caa6090	WEBSITE	2026-10-25	40000.00	500.00	39500.00	PARTIALLY_PAID	CANCELLED	2026-10-25 23:37:35.841892+05:30	Bulk imported on 2026-10-25 (Ref: Sl No 4.0)	2026-10-25 23:37:35.72326+05:30	2026-10-25 23:52:29.732426+05:30	\N	\N	\N	0.00	400.00	39600.00	jharkhand	f	2026-10-25 23:52:29.732426+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
c59e5da3-5272-46c4-8f1f-7810b7647c8c	SO-2026-0028	5242338c-3887-56db-b86c-c59deae26654	a11df6a4-62e1-4193-9943-fc6940fc3cc5	3fedfba5-e644-5643-9283-061b36dbf36c	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	WEBSITE	2026-10-25	11800.00	5000.00	6800.00	PARTIALLY_PAID	CANCELLED	2026-10-25 23:04:54.405026+05:30	\N	2026-10-25 23:04:54.377324+05:30	2026-10-25 23:52:37.604036+05:30	\N	\N	\N	0.00	200.00	11600.00	jharkhand	t	2026-10-25 23:52:37.604036+05:30	de526836-5e73-49d7-9be3-8ad07caa6090	\N
\.


--
-- Data for Name: sales_order_audit_log; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.sales_order_audit_log (audit_id, sales_order_id, actor_user_id, action_type, linked_task_id, previous_status, deletion_reason, created_at) FROM stdin;
3d4734a8-9983-478f-a274-622fae91a762	36311f50-9a3c-4203-a79f-6b59eb66a8dc	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	bf7aa794-c1d2-452e-b6d3-ba838dd10b02	order:CONFIRMED|task:ASSIGNED	\N	2026-10-25 23:01:44.739141+05:30
a285d157-e097-465d-8d34-53f7c0503fc5	3b514f9b-87f3-410d-b475-da6c8d41d9f7	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	eaeea2ed-76f7-4b5a-a5be-a9f304b72275	order:CONFIRMED|task:ASSIGNED	\N	2026-10-25 23:01:48.002443+05:30
27a5481b-1563-4c5f-bda4-3c29b96c5be7	1f859330-e63f-40f4-ba79-abf2d3714b28	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	2f3b7575-2066-493a-a62c-fc95be74d0fb	order:CONFIRMED|task:ASSIGNED	\N	2026-10-25 23:01:58.070864+05:30
a2cac4b4-ebf2-4fd9-93b9-082178005dce	249e834e-1cd7-45b5-8707-f78e0ccea2a3	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	950cc940-dbb1-45e3-a4fc-276eced83899	order:CONFIRMED|task:ASSIGNED	\N	2026-10-25 23:02:05.343881+05:30
1b93146e-b6d3-4099-bb84-a9a62b421428	b7dc6d32-f9ea-4222-adf2-f68aa48f16f1	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	8553d61d-cce7-4877-8474-9a990c4ee4ec	order:CONFIRMED|task:ASSIGNED	\N	2026-10-25 23:02:09.213476+05:30
ee62b427-8ed9-480d-a816-9dc98c52465c	e50488bf-3e95-449e-ac02-2af61871b164	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	2df25880-1b91-4ed4-9eb4-9aa54cb56f53	order:CONFIRMED|task:ASSIGNED	\N	2026-10-25 23:52:16.203462+05:30
c0edcf04-c882-4cae-9d5d-e2111a064e7c	4af7b6bf-3ff9-41b8-bb28-5cbc588eb07f	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	2bed4f2b-61f3-45b0-bf20-474a212be9e3	order:CONFIRMED|task:ASSIGNED	\N	2026-10-25 23:52:19.692351+05:30
7e8ebd2a-42ad-4f2c-888a-23db14075737	082cc2aa-0177-42ae-b670-03e815776e28	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	71ae120b-7250-43d3-a092-ca60b8366bfa	order:CONFIRMED|task:ASSIGNED	\N	2026-10-25 23:52:22.243153+05:30
729a3148-5cfa-4e05-9cb2-d4a7288c9da5	df7f3086-b111-4174-97a6-3f0d5966a2c3	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	ca0c550f-6f0e-4b06-8466-66fc8b221831	order:CONFIRMED|task:ASSIGNED	\N	2026-10-25 23:52:24.971144+05:30
87d21472-dbba-440e-b960-e11ea23d1173	98c27bf9-6ba5-4db2-a536-842ed7aad7e4	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	733b35e2-4330-4588-aa1f-5ec8d6df279c	order:CONFIRMED|task:ASSIGNED	\N	2026-10-25 23:52:27.691696+05:30
17ae9b40-80ef-4605-bde9-0600262f8db7	c70382c1-9155-480c-b725-a4a10ba56020	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	5975e799-fb23-4f30-8f31-4338ed37ee4a	order:CONFIRMED|task:ASSIGNED	\N	2026-10-25 23:52:29.732426+05:30
27e2b83c-b6d8-4620-81f9-e5f0ae3abd85	c59e5da3-5272-46c4-8f1f-7810b7647c8c	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	680e84cc-4054-49d2-b147-d6a86b5b9a13	order:CONFIRMED|task:ASSIGNED	\N	2026-10-25 23:52:37.604036+05:30
80bd3bca-f71a-4820-91c1-2488d3d0ca52	d2fee853-0b72-4c9f-94eb-09c7022a2364	de526836-5e73-49d7-9be3-8ad07caa6090	SUPER_ADMIN_OVERRIDE_DELETE	e5837191-599a-4c9d-ac0d-58f9e442045c	order:CONFIRMED|task:APPROVED	giugiu	2026-10-26 00:38:04.067502+05:30
4a4b911b-43b4-42c5-9c18-8f6d4e97ae65	280da9e2-783d-4bbe-bde3-d30755a0eac6	de526836-5e73-49d7-9be3-8ad07caa6090	SUPER_ADMIN_OVERRIDE_DELETE	3ca55838-d953-4175-a37a-780ff438c869	order:CONFIRMED|task:APPROVED	dummy entry	2026-10-31 12:06:12.829026+05:30
516a4885-0c9b-4e78-a71e-ab6a28fbe75e	4b8fbf7e-35bf-420c-a022-9db4436abe34	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	4ea8e868-36ad-4bf1-8faa-6ab242e954bd	order:CONFIRMED|task:ASSIGNED	dummy entry	2026-10-31 12:06:20.914963+05:30
3e5ac4bd-9ee7-490b-ac7b-73de2e908c4a	d028df71-155b-41e6-84ce-f7619697c96b	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	3997d4d2-bfb5-4a06-8cec-929270aeb419	order:CONFIRMED|task:ASSIGNED	dummy entry	2026-10-31 12:06:31.54437+05:30
fa76a6d9-4085-43e6-8556-f75f7a64f9ed	3a42eeeb-172d-486b-ad8a-98d6b647a46e	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	db093cfd-6c3b-473c-ae66-9b295924aa36	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:07:01.349678+05:30
2f7b1c7b-0d18-40b5-be7d-68ca0da83eba	b237ea09-b7b5-401f-8b12-e00a530a525c	de526836-5e73-49d7-9be3-8ad07caa6090	SUPER_ADMIN_OVERRIDE_DELETE	6bccf11d-68fe-4020-bac4-820936578bec	order:CONFIRMED|task:APPROVED	dummy entry	2026-10-31 12:07:16.834664+05:30
dfd6a2be-aabc-4fe1-b351-d70f460d6a12	2de435d8-b74d-4d31-95f3-2d4a37701ac9	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	058b6bc8-9285-43fd-8c52-67532eb40ac6	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:07:21.439531+05:30
9f0323b1-4a9d-4d56-b7fa-5117524f38cf	027b8d57-fce7-4f60-ae50-a8ccd7cb5e03	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	e0a66aa9-91bf-4214-85e2-5d8e270f2b23	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:07:26.169987+05:30
74f0ba2b-5afe-4b36-bc39-ba58fe726ac1	c7c8d7f1-26f9-46d7-ac24-0ba21db409eb	de526836-5e73-49d7-9be3-8ad07caa6090	SUPER_ADMIN_OVERRIDE_DELETE	86b46c7c-0c6b-4fa4-bff7-e428dc2ba239	order:CONFIRMED|task:APPROVED	dummy entry	2026-10-31 12:07:34.927719+05:30
fd05e3c7-2bc1-46cf-95d2-e1d1dd5fa259	7c0282ad-764c-41f0-950c-00d0db5b8464	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	543de9f0-dcb8-47b4-b98f-5b194e1258f3	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:07:38.988466+05:30
338452f5-ad92-4620-9555-706be66cc7ac	be4a1a11-c14b-40cf-9032-835e278465d2	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	f25069b3-5013-4ebb-82ef-cea01267657c	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:07:42.118273+05:30
95f2313d-9ed5-4207-b08a-ead8dd5e10a1	3580eeaa-4a41-478a-b9bf-750d201462ba	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	38ce8f41-9a04-40d2-acc8-543390e99cbf	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:07:44.815731+05:30
53dd9325-43d0-4944-a88a-2edc5579b261	990fefe7-5e97-43d2-a8fb-071848f09bc2	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	f05bb899-190f-40b0-b993-038e3011bf0b	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:07:47.483113+05:30
017d5cd3-c624-426d-8e6f-8623d834b8c0	49573950-2950-4bd2-9b3f-8b0b72781f51	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	68bae788-12d3-40a8-97be-06ec36f8772e	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:07:50.067049+05:30
198a24ff-d824-4a90-aaeb-73fe08e41fb6	216eccee-dfbb-48f0-8a63-217ba2b167eb	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	e32bf79c-e6e2-4615-b1f2-8040247c3f18	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:07:52.658268+05:30
580c9d8d-bec8-48be-a073-f2e7d6e5a4de	ce006ca7-42c0-4b87-85bc-bd92fe729ffb	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	a939e2c4-35b9-47c9-9f8a-bc448c5bb877	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:07:56.549579+05:30
2089cbc7-ee4f-4a47-a39d-60fa6fc80e76	a8c86af8-353e-45ad-be11-10187e517cf7	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	4adf326f-6dda-4684-ab74-874667a59a0b	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:07:59.544928+05:30
3bafd401-3223-481f-ab08-fc3ee4b4efc4	78f5dcf1-214e-4075-8501-fb05af2d7bd8	de526836-5e73-49d7-9be3-8ad07caa6090	SUPER_ADMIN_OVERRIDE_DELETE	9b78f07f-d6c0-41ce-a08e-a255e0426fe9	order:CONFIRMED|task:APPROVED	Dummy entry	2026-10-31 12:08:09.740188+05:30
69dbb34f-3761-4317-853f-5e02c4362e94	a408e780-d55a-4137-a4a2-b8a90bd1bc29	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	da56b220-e470-4487-a407-48645b60dbdc	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:08:13.643257+05:30
3993a6d2-d1d8-4428-9c80-c86ef7e83832	ce897913-8de9-422d-8d1f-f415cf3504a7	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	bbbc717f-d53c-4475-a7ea-9ff5066ab79a	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:08:16.495194+05:30
f75b4f3a-1906-4132-9d71-f6a46492b32a	c3f09177-7fc9-436b-bdd5-d177c419d38e	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	b5fdb615-3dba-4a07-bcc8-ebcd273928f0	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:08:18.874935+05:30
dc212a01-c1fe-4ee4-9368-8fea2bd55efe	7558b3f8-00f9-4897-a5b2-5d01f137555c	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	dece3eea-3f5b-46f5-9d7c-29ad9334097c	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:08:21.379945+05:30
1b7ed8d4-b9b8-49df-8858-0c5a7652a910	e78da1c9-8d92-4e76-bc36-700770eecaab	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	0eef383e-ac4b-4541-a9a7-e0b98de5d548	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:08:23.87694+05:30
52b776e3-87c0-4ab4-b666-7a3531fe1b89	9f937f0a-66bf-4635-ba53-739203287a4c	de526836-5e73-49d7-9be3-8ad07caa6090	SOFT_DELETE	f7e3cf19-1c1f-4a8a-a90a-ad89aae49adb	order:CONFIRMED|task:ASSIGNED	\N	2026-10-31 12:08:28.590881+05:30
\.


--
-- Data for Name: service_master; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.service_master (service_id, service_code, service_name, category, description, base_price, govt_fee, standard_turnaround_days, status, created_at, updated_at) FROM stdin;
40b5a081-65fb-5e83-819f-fa4a49c7977f	TRADE_LICENSE	Trade License	LICENCE	Municipal corporation business trade license and renewal	15000.00	2500.00	15	ACTIVE	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
79ba81bc-3247-59a3-9896-ce9766c46600	SHOP_ACT	Shop Act	REGISTRATION	State shops and commercial establishments registration (Gumasta)	8000.00	1200.00	7	ACTIVE	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
3fedfba5-e644-5643-9283-061b36dbf36c	CLRA	CLRA Registration	COMPLIANCE	Contract Labour Regulation and Abolition statutory licence	25000.00	5000.00	21	ACTIVE	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
a22e7dcd-6495-5311-883c-93fc61c87ef4	PCB	PCB Consent	LICENCE	Pollution Control Board Consent to Establish and Operate (CTE/CTO)	40000.00	15000.00	30	ACTIVE	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
c7adcc88-0569-57e1-af74-a85737bdc641	CLINICAL_ESTABLISHMENT	Clinical Establishment	LICENCE	Clinical Establishment Act registration for clinics, hospitals, and diagnostic labs	35000.00	10000.00	25	ACTIVE	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
e0a8e4b8-3750-54ba-be0b-fa21906d8697	PESO	PESO	LICENCE	Petroleum and Explosives Safety Organisation statutory approvals	60000.00	25000.00	45	ACTIVE	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
b42c5d8d-2820-566b-bfad-26a329fc914f	LLP	LLP	INCORPORATION	Limited Liability Partnership registration with MCA (FiLLiP)	10000.00	2000.00	10	ACTIVE	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
547b955f-8d2e-5abd-9151-4c33ae212cf4	OPC	One Person Company	INCORPORATION	One Person Company incorporation with single shareholder & nominee	11000.00	2500.00	10	ACTIVE	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
e1ad76a3-a315-4c76-b64e-77cbc7b9a6d9	FSSAI	FSSAI	LICENCE	\N	0.00	0.00	15	ACTIVE	2026-09-29 01:04:39.46415+05:30	2026-09-29 01:04:39.46415+05:30
55e21cf3-8fca-4241-b8c9-1f5699520d12	ESI	ESI	LICENCE	Esi	0.00	0.00	15	ACTIVE	2026-10-10 02:43:09.896819+05:30	2026-10-10 02:43:09.896819+05:30
\.


--
-- Data for Name: service_required_document; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.service_required_document (doc_config_id, service_id, document_code, document_name, is_mandatory, display_order, created_at, updated_at) FROM stdin;
2eed050a-f46e-49d3-99a2-ff0092de01cd	40b5a081-65fb-5e83-819f-fa4a49c7977f	PAN	PAN Card of Entity/Proprietor	t	10	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
e10ef6c7-9fa5-40eb-94a6-13d53654ac8e	40b5a081-65fb-5e83-819f-fa4a49c7977f	AADHAAR	Aadhaar Card of Applicant	t	20	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
ca0521dd-4050-444d-b9d8-59c2a6ea3eb4	40b5a081-65fb-5e83-819f-fa4a49c7977f	RENT_AGREEMENT	Registered Rent Agreement / NOC	t	30	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
05658b29-d7b3-4fe0-a7a7-70ab77493ae8	40b5a081-65fb-5e83-819f-fa4a49c7977f	PROPERTY_TAX	Property Tax Receipt	t	40	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
a2b3f43f-d6f3-4499-9850-671324d261db	40b5a081-65fb-5e83-819f-fa4a49c7977f	ELECTRICITY_BILL	Recent Electricity Bill	t	50	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
83c7d406-2567-473d-abfa-eb6a22fdea9f	79ba81bc-3247-59a3-9896-ce9766c46600	PAN	PAN Card of Business Owner	t	10	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
040907b3-9107-4553-b984-dc58951c299c	79ba81bc-3247-59a3-9896-ce9766c46600	AADHAAR	Aadhaar Card of Authorized Person	t	20	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
3df357c4-6650-4794-a8e9-3f8684a7d0ff	79ba81bc-3247-59a3-9896-ce9766c46600	GEO_IMAGE	Geo-tagged photo of shop with signboard	t	30	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
de4789c1-dbe0-4430-9e58-ed4118c3820e	79ba81bc-3247-59a3-9896-ce9766c46600	RENT_AGREEMENT	Rent Agreement / Ownership Proof	t	40	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
32521bf4-b231-46a9-89ab-1d48520e4dba	3fedfba5-e644-5643-9283-061b36dbf36c	COI	Certificate of Incorporation	t	10	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
f86b20e6-1a1b-4cc5-82f9-58d515b31c1f	3fedfba5-e644-5643-9283-061b36dbf36c	FORM_V	Form V issued by Principal Employer	t	20	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
de043f88-d393-46db-b7ba-29c602d44510	3fedfba5-e644-5643-9283-061b36dbf36c	PAN	Company PAN Card	t	30	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
159a6f29-7e3f-40cf-8920-e76f94df9314	3fedfba5-e644-5643-9283-061b36dbf36c	AGREEMENT	Master Services Agreement with Principal Employer	t	40	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
794a126b-6b85-4632-b440-4dfef0ad265d	a22e7dcd-6495-5311-883c-93fc61c87ef4	SITE_PLAN	Site Layout and Plant Machinery Plan	t	10	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
bbd45db1-1a9c-4fb7-b3a3-f5d8856e9918	a22e7dcd-6495-5311-883c-93fc61c87ef4	PROJECT_REPORT	Detailed Project Report on Emissions/Effluents	t	20	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
f2d541f1-29f3-4257-9e9f-1ab0a422af88	a22e7dcd-6495-5311-883c-93fc61c87ef4	LAND_DOCS	Land Possession / Ownership Documents	t	30	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
19fdef0d-5c8d-4bde-ab04-d41a989019d1	a22e7dcd-6495-5311-883c-93fc61c87ef4	COI	Certificate of Incorporation / Registration	t	40	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
9492c062-528e-45da-8283-e068bc317573	a22e7dcd-6495-5311-883c-93fc61c87ef4	WATER_NOC	Water Connection NOC / Supply Bill	f	50	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
5703d922-70fc-4333-b16e-a43df7c3fdf8	c7adcc88-0569-57e1-af74-a85737bdc641	DOCTOR_DEGREE	Medical Council Registration & Degrees of Doctors	t	10	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
331e8a0e-849e-4b60-980b-0dfcceafe946	c7adcc88-0569-57e1-af74-a85737bdc641	STAFF_DETAILS	Nursing and Paramedical Staff Credentials	t	20	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
000ef02b-984d-4d14-89d4-cec2b25f834e	c7adcc88-0569-57e1-af74-a85737bdc641	FIRE_NOC	Fire Department Safety NOC	t	30	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
ac7fbd89-1683-4a6d-a23d-7e2434730b3b	c7adcc88-0569-57e1-af74-a85737bdc641	BM_WASTE	Bio-Medical Waste Management Agreement	t	40	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
77c9b8d6-284c-4e41-be77-51232ec33110	e0a8e4b8-3750-54ba-be0b-fa21906d8697	EXPLOSIVE_PLAN	Approved Storage and Handling Blueprint	t	10	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
1459e34b-1281-42d4-bf0a-eaa4c34628f9	e0a8e4b8-3750-54ba-be0b-fa21906d8697	SAFETY_CERT	Competent Person Safety & Fabricator Certificate	t	20	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
b442a856-0e57-4ff6-8a95-6e6e21d2a87d	e0a8e4b8-3750-54ba-be0b-fa21906d8697	DM_NOC	District Magistrate No Objection Certificate	t	30	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
bb388e3f-dc86-4918-b088-afd878e4ae18	e0a8e4b8-3750-54ba-be0b-fa21906d8697	COI	Corporate Entity Incorporation Proof	t	40	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
19c35d8d-8a6f-4117-86a9-07747f7083f1	b42c5d8d-2820-566b-bfad-26a329fc914f	PAN_PARTNERS	PAN Cards of Designated Partners	t	10	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
ef654220-c79d-4b54-a9ad-ed9a9446e2c4	b42c5d8d-2820-566b-bfad-26a329fc914f	ID_PROOF	Identity & Address Proofs of Partners	t	20	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
2717d59a-0562-468a-b9eb-a50598e53b5c	b42c5d8d-2820-566b-bfad-26a329fc914f	OFFICE_PROOF	Registered Office Address Proof & NOC	t	30	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
7e63c8be-ba69-44ec-9973-d816052907b5	b42c5d8d-2820-566b-bfad-26a329fc914f	LLP_AGREEMENT	Executed LLP Agreement	t	40	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
1ff67506-fac6-4a70-9784-efff49e912cc	547b955f-8d2e-5abd-9151-4c33ae212cf4	PAN_MEMBER	PAN Card of Member and Nominee	t	10	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
0ec3df23-e5e4-4baa-a064-2da0dfe3d516	547b955f-8d2e-5abd-9151-4c33ae212cf4	NOMINEE_CONSENT	Form INC-3 Nominee Consent Letter	t	20	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
e6b7cdb5-c8cf-4e73-8b51-c2371b9d06b9	547b955f-8d2e-5abd-9151-4c33ae212cf4	OFFICE_PROOF	Registered Office Utility Bill & NOC	t	30	2026-09-23 01:56:03.529867+05:30	2026-09-23 01:56:03.529867+05:30
\.


--
-- Data for Name: source_master; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.source_master (source_id, source_code, source_name, description, status, is_system, created_at, updated_at) FROM stdin;
e2d4b3ae-cb0e-424e-ad00-532840e66e2d	WEBSITE	Website	Direct enquiries from company website	ACTIVE	t	2026-11-01 19:00:09.908589+05:30	2026-11-01 19:00:09.908589+05:30
88405e2b-6dd7-4dd7-a8a2-996eebc1507e	REFERRAL	Referral	Client referrals and partner recommendations	ACTIVE	t	2026-11-01 19:00:09.908589+05:30	2026-11-01 19:00:09.908589+05:30
d17b6c8f-cc72-414e-8a16-aa1d30935a75	DIRECT	Direct	Direct walk-in or outbound sales contact	ACTIVE	t	2026-11-01 19:00:09.908589+05:30	2026-11-01 19:00:09.908589+05:30
53ad4eba-41ff-49f8-9ea4-12c5dc2088be	JUSTDIAL	Justdial	Lead acquisition via Justdial platform	ACTIVE	t	2026-11-01 19:00:09.908589+05:30	2026-11-01 19:00:09.908589+05:30
22702683-d181-4184-983b-d6881ffbdfe7	INDIAMART	IndiaMART	Lead acquisition via IndiaMART marketplace	ACTIVE	t	2026-11-01 19:00:09.908589+05:30	2026-11-01 19:00:09.908589+05:30
8b6c31d8-3b85-460b-93b3-10fdda3e4031	OTHERS	Others	Other miscellaneous acquisition channels	ACTIVE	t	2026-11-01 19:00:09.908589+05:30	2026-11-01 19:00:09.908589+05:30
ba087cc9-fc8e-45fb-8085-2067615b1d58	MUSKAN_MAAM	Muskan Maam	\N	ACTIVE	f	2026-11-01 19:23:13.007413+05:30	2026-11-01 19:23:13.007413+05:30
25616f75-bf97-4781-9e0b-44477aa222d1	DEEPAK_SIR	Deepak Sir	\N	ACTIVE	f	2026-11-01 19:23:37.368258+05:30	2026-11-01 19:23:37.368258+05:30
de70b6a4-9c29-4442-b5b1-07e924e2df98	PUNEET_SIR	Puneet Sir	\N	ACTIVE	f	2026-11-01 19:23:56.829683+05:30	2026-11-01 19:23:56.829683+05:30
\.


--
-- Data for Name: task_conversation_message; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.task_conversation_message (message_id, sales_order_id, author_user_id, message_type, message_text, author_name, author_employee_code, author_department_name, author_role_name, event_type, event_metadata, idempotency_key, created_at, originating_module) FROM stdin;
4703abbb-a973-417a-af6c-0d94328f09aa	77b1df77-3aab-4394-b737-abc82994eb3a	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	COMMENT	VUYOU	Karishma Upadhyay	CG0004	Sales	Senior Executive	\N	\N	\N	2026-09-23 23:42:54.314988+05:30	\N
a07174cf-10c5-4daf-8137-181a764cb0b7	9f937f0a-66bf-4635-ba53-739203287a4c	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	COMMENT	vdfb kjgfd	Karishma Upadhyay	CG0004	Sales	Senior Executive	\N	\N	\N	2026-09-30 11:16:20.182113+05:30	\N
099ce54b-0208-4e76-aef5-716d1a340db7	7558b3f8-00f9-4897-a5b2-5d01f137555c	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	COMMENT	hello hunny bunny	Karishma Upadhyay	CG0004	Sales	Senior Executive	\N	\N	\N	2026-10-07 01:33:59.33512+05:30	\N
0690e199-1031-4bb3-af5e-9baf42ddb369	b237ea09-b7b5-401f-8b12-e00a530a525c	0438f197-65cc-4fb2-8667-bdaceee1db81	COMMENT	delay ho raha hai bhaii	Deepak Kumar	CG0005	Operations	Senior Executive	\N	\N	\N	2026-09-26 01:57:57.173187+05:30	\N
954c7eb5-0d5c-4c43-91b1-b06abe16282b	b237ea09-b7b5-401f-8b12-e00a530a525c	0438f197-65cc-4fb2-8667-bdaceee1db81	COMMENT	are bhaii bhaii	Deepak Kumar	CG0005	Operations	Senior Executive	\N	\N	\N	2026-09-26 02:14:02.775174+05:30	\N
fee743c2-f851-4cdf-a357-34fced9fe708	280da9e2-783d-4bbe-bde3-d30755a0eac6	0438f197-65cc-4fb2-8667-bdaceee1db81	COMMENT	NOT POSSIBLE	Deepak Kumar	CG0005	Operations	Senior Executive	\N	\N	\N	2026-09-28 16:02:14.873895+05:30	\N
eaee8387-8eea-499d-9684-c45721287bbc	c7c8d7f1-26f9-46d7-ac24-0ba21db409eb	de526836-5e73-49d7-9be3-8ad07caa6090	COMMENT	DHFGBLH	Super Admin	CG0001	Administration	Director	\N	\N	\N	2026-09-29 16:57:03.827507+05:30	\N
3ffe5439-abb7-44da-9f31-47e4ac0da446	c7c8d7f1-26f9-46d7-ac24-0ba21db409eb	de526836-5e73-49d7-9be3-8ad07caa6090	COMMENT	GFDGFD,UF	Super Admin	CG0001	Administration	Director	\N	\N	\N	2026-09-29 17:00:45.74438+05:30	\N
c85fc482-976d-4078-ba31-55f50b8cd5d4	7c0282ad-764c-41f0-950c-00d0db5b8464	0438f197-65cc-4fb2-8667-bdaceee1db81	COMMENT	jckthdctluvj	Deepak Kumar	CG0005	Operations	Senior Executive	\N	\N	\N	2026-09-30 10:49:18.104984+05:30	\N
fdfdf6af-b4d4-48cc-9842-a53936d30ac9	c3f09177-7fc9-436b-bdd5-d177c419d38e	de526836-5e73-49d7-9be3-8ad07caa6090	COMMENT	hello start the conversation	Super Admin	CG0001	Administration	Director	\N	\N	c3f09177-7fc9-436b-bdd5-d177c419d38e_1791483890491_l80z9wh	2026-10-08 23:54:50.534083+05:30	\N
f2fd363f-ff78-4990-bf87-c86f67e88cba	c3f09177-7fc9-436b-bdd5-d177c419d38e	de526836-5e73-49d7-9be3-8ad07caa6090	COMMENT	hello secound conversation	Super Admin	CG0001	Administration	Director	\N	\N	c3f09177-7fc9-436b-bdd5-d177c419d38e_1791483918467_ke1bxbu	2026-10-08 23:55:18.48581+05:30	\N
a80c2df1-c5cd-4e69-ac2b-ff2026e2a900	c3f09177-7fc9-436b-bdd5-d177c419d38e	de526836-5e73-49d7-9be3-8ad07caa6090	COMMENT	last conversation	Super Admin	CG0001	Administration	Director	\N	\N	c3f09177-7fc9-436b-bdd5-d177c419d38e_1791483943254_ufjvrw8	2026-10-08 23:55:43.270509+05:30	\N
a7baea7c-6b13-41c4-8ae8-b5922a00a9b1	c3f09177-7fc9-436b-bdd5-d177c419d38e	0438f197-65cc-4fb2-8667-bdaceee1db81	COMMENT	hello testing	Deepak Kumar	CG0005	Operations	Senior Executive	\N	\N	c3f09177-7fc9-436b-bdd5-d177c419d38e_1791484265220_zdezq5d	2026-10-09 00:01:05.271678+05:30	\N
2d3a5649-207f-4924-b896-6b0416e95f4f	c3f09177-7fc9-436b-bdd5-d177c419d38e	0438f197-65cc-4fb2-8667-bdaceee1db81	COMMENT	kya bhaii sucessfull ho gya kya	Deepak Kumar	CG0005	Operations	Senior Executive	\N	\N	c3f09177-7fc9-436b-bdd5-d177c419d38e_1791486373520_sgdwp7z	2026-10-09 00:36:13.554952+05:30	\N
7d4b85a1-9e86-4d73-b914-ada45de8a35f	c3f09177-7fc9-436b-bdd5-d177c419d38e	de526836-5e73-49d7-9be3-8ad07caa6090	COMMENT	haa siir	Super Admin	CG0001	Administration	Director	\N	\N	c3f09177-7fc9-436b-bdd5-d177c419d38e_1791486386779_nohy9qo	2026-10-09 00:36:26.799785+05:30	\N
26cd87cf-e90f-48f1-93ed-2632fab94f70	c3f09177-7fc9-436b-bdd5-d177c419d38e	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	COMMENT	hello gyus	Karishma Upadhyay	CG0004	Sales	Senior Executive	\N	\N	c3f09177-7fc9-436b-bdd5-d177c419d38e_1791486461336_rswpnfv	2026-10-09 00:37:41.385078+05:30	\N
79edcd15-ff81-4a0d-9170-a725881c6bae	c3f09177-7fc9-436b-bdd5-d177c419d38e	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	COMMENT	kya bhaii moj kr di lala heheh	Karishma Upadhyay	CG0004	Sales	Senior Executive	\N	\N	c3f09177-7fc9-436b-bdd5-d177c419d38e_1791488056502_adlki21	2026-10-09 01:04:16.537733+05:30	\N
d4c0b222-1dff-49d8-a607-e8bbd34e5bf8	c3f09177-7fc9-436b-bdd5-d177c419d38e	de526836-5e73-49d7-9be3-8ad07caa6090	COMMENT	or bhaiiiii aa gya swaad	Super Admin	CG0001	Administration	Director	\N	\N	c3f09177-7fc9-436b-bdd5-d177c419d38e_1791533368427_jku4hhk	2026-10-09 13:39:28.465619+05:30	ADMIN
cc177bc6-181a-463d-b533-194e0c606e9b	c3f09177-7fc9-436b-bdd5-d177c419d38e	de526836-5e73-49d7-9be3-8ad07caa6090	COMMENT	heheh haaji	Super Admin	CG0001	Administration	Director	\N	\N	c3f09177-7fc9-436b-bdd5-d177c419d38e_1791534296250_179uv7c	2026-10-09 13:54:56.270212+05:30	ADMIN
5c59378a-01b7-411c-9a22-8f4ebaa95a06	c3f09177-7fc9-436b-bdd5-d177c419d38e	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	COMMENT	ky hai	Karishma Upadhyay	CG0004	Sales	Senior Executive	\N	\N	c3f09177-7fc9-436b-bdd5-d177c419d38e_1791534311166_y1e1aa6	2026-10-09 13:55:11.209514+05:30	SALES
3b719dcb-f8fd-4232-86de-b2a278784788	e78da1c9-8d92-4e76-bc36-700770eecaab	de526836-5e73-49d7-9be3-8ad07caa6090	COMMENT	next to next	Super Admin	CG0001	Administration	Director	\N	\N	e78da1c9-8d92-4e76-bc36-700770eecaab_1791534332747_j8paap9	2026-10-09 13:55:32.769987+05:30	ADMIN
45fd985a-b112-40a7-8b4b-983d46f91008	ce897913-8de9-422d-8d1f-f415cf3504a7	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0017' confirmed and assigned to Mansi Singhal (CG0003) by Super Admin.	Super Admin	CG0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "CG0003"}	\N	2026-10-09 19:03:35.685795+05:30	\N
f876e62d-99d2-48a3-be3c-0fefdafde55e	ce897913-8de9-422d-8d1f-f415cf3504a7	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Task reassigned from Mansi Singhal (CG0003) to Deepak Kumar (CG0005) by Super Admin (CG0001). Reason: hv cftc	Super Admin	CG0001	Administration	Director	REASSIGNMENT	{"action": "TASK_REASSIGNED", "previous_assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "previous_assignee_name": "Mansi Singhal", "new_assignee_id": "0438f197-65cc-4fb2-8667-bdaceee1db81", "new_assignee_name": "Deepak Kumar", "new_assignee_code": "CG0005", "reason": "hv cftc"}	\N	2026-10-09 19:19:17.922373+05:30	\N
e3dcc3d4-9983-4777-9d6a-3092c4e3bc71	ce897913-8de9-422d-8d1f-f415cf3504a7	de526836-5e73-49d7-9be3-8ad07caa6090	COMMENT	hb ygv	Super Admin	CG0001	Administration	Director	\N	\N	ce897913-8de9-422d-8d1f-f415cf3504a7_1791553766011_05zzzr4	2026-10-09 19:19:26.029788+05:30	ADMIN
180bbdcb-9834-4644-95cf-569ac940d175	ce897913-8de9-422d-8d1f-f415cf3504a7	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Task reassigned from Deepak Kumar (CG0005) to Abhishek Kumar (CG0007) by Super Admin (CG0001). Reason: vfty6cfty	Super Admin	CG0001	Administration	Director	REASSIGNMENT	{"action": "TASK_REASSIGNED", "previous_assignee_id": "0438f197-65cc-4fb2-8667-bdaceee1db81", "previous_assignee_name": "Deepak Kumar", "new_assignee_id": "dcdee779-494b-4fe7-afa1-d3b66c784fbb", "new_assignee_name": "Abhishek Kumar", "new_assignee_code": "CG0007", "reason": "vfty6cfty"}	\N	2026-10-09 19:21:57.479945+05:30	\N
d4202383-4bbd-4e33-b2ec-c142603b8b38	a408e780-d55a-4137-a4a2-b8a90bd1bc29	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0018' confirmed and assigned to Mansi Singhal (CG0003) by Super Admin.	Super Admin	CG0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "CG0003"}	\N	2026-10-09 19:27:56.248847+05:30	\N
ed97dba1-2950-4ca0-99cd-af1b90b666ad	ce897913-8de9-422d-8d1f-f415cf3504a7	de526836-5e73-49d7-9be3-8ad07caa6090	COMMENT	CALL AKASH 456789	Super Admin	CG0001	Administration	Director	\N	\N	ce897913-8de9-422d-8d1f-f415cf3504a7_1791554673935_8melwz7	2026-10-09 19:34:33.962955+05:30	ADMIN
168f3c22-3abb-42e9-bdbd-7a5d27ee652f	78f5dcf1-214e-4075-8501-fb05af2d7bd8	8554d145-bdd4-4ee6-b821-74b73cfe40bf	COMMENT	chalo bhaiilog kaam aagya hai	Reeya Soni	EP0001	Sales	Senior Executive	\N	\N	\N	2026-10-10 02:44:56.472408+05:30	SALES
84555100-a7ac-4f26-9b8b-7abf4c7d2b58	78f5dcf1-214e-4075-8501-fb05af2d7bd8	8554d145-bdd4-4ee6-b821-74b73cfe40bf	SYSTEM_EVENT	Order 'SO-2026-0019' confirmed and assigned to Mansi Singhal (GC0003) by Reeya Soni.	Reeya Soni	EP0001	Sales	Senior Executive	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-10 02:44:56.482069+05:30	\N
5c536fb5-0501-4113-9e7f-8ffd65508f28	78f5dcf1-214e-4075-8501-fb05af2d7bd8	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	SYSTEM_EVENT	Task reassigned from Mansi Singhal (GC0003) to Hrithik Choudhary (GC0008) by Mansi Singhal (GC0003). Reason: hrithik ye task aab tm dekhoge	Mansi Singhal	GC0003	Operations	Manager	REASSIGNMENT	{"action": "TASK_REASSIGNED", "previous_assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "previous_assignee_name": "Mansi Singhal", "new_assignee_id": "65b43201-4875-4caa-a601-b0b535019b48", "new_assignee_name": "Hrithik Choudhary", "new_assignee_code": "GC0008", "reason": "hrithik ye task aab tm dekhoge"}	\N	2026-10-10 02:51:37.01459+05:30	\N
283cab07-3b8d-4c32-953c-acc6bcd70408	78f5dcf1-214e-4075-8501-fb05af2d7bd8	65b43201-4875-4caa-a601-b0b535019b48	COMMENT	site naii chal rahahia	Hrithik Choudhary	GC0008	Operations	Executive	\N	\N	\N	2026-10-10 02:52:52.429684+05:30	\N
f0e42b93-7aac-43af-8128-e3019ed3e179	78f5dcf1-214e-4075-8501-fb05af2d7bd8	65b43201-4875-4caa-a601-b0b535019b48	SYSTEM_EVENT	Task status changed from ASSIGNED to IN_PROGRESS by Hrithik Choudhary (GC0008).	Hrithik Choudhary	GC0008	Operations	Executive	STATUS_CHANGE	{"action": "STATUS_CHANGE", "old_status": "ASSIGNED", "new_status": "IN_PROGRESS", "comment": null}	\N	2026-10-10 02:53:04.333608+05:30	\N
6aa9a9cf-6480-435f-affd-2f589d76ebad	78f5dcf1-214e-4075-8501-fb05af2d7bd8	65b43201-4875-4caa-a601-b0b535019b48	SYSTEM_EVENT	Task status changed from IN_PROGRESS to READY_FOR_SUBMISSION by Hrithik Choudhary (GC0008).	Hrithik Choudhary	GC0008	Operations	Executive	STATUS_CHANGE	{"action": "STATUS_CHANGE", "old_status": "IN_PROGRESS", "new_status": "READY_FOR_SUBMISSION", "comment": null}	\N	2026-10-10 02:53:17.242599+05:30	\N
cdcbe77f-7c89-48cd-b954-81501a2b0ea4	78f5dcf1-214e-4075-8501-fb05af2d7bd8	65b43201-4875-4caa-a601-b0b535019b48	COMMENT	done mera kaam ho gy ahai	Hrithik Choudhary	GC0008	Operations	Executive	\N	\N	\N	2026-10-10 02:53:42.079597+05:30	\N
82fec869-8143-4880-880e-67cb6b0c61e5	78f5dcf1-214e-4075-8501-fb05af2d7bd8	65b43201-4875-4caa-a601-b0b535019b48	SYSTEM_EVENT	Task status changed from READY_FOR_SUBMISSION to SUBMITTED by Hrithik Choudhary (GC0008).	Hrithik Choudhary	GC0008	Operations	Executive	STATUS_CHANGE	{"action": "STATUS_CHANGE", "old_status": "READY_FOR_SUBMISSION", "new_status": "SUBMITTED", "comment": null}	\N	2026-10-10 02:53:20.323383+05:30	\N
03ef8bb0-6bfb-4d87-b6e2-cb8c036a4313	78f5dcf1-214e-4075-8501-fb05af2d7bd8	65b43201-4875-4caa-a601-b0b535019b48	SYSTEM_EVENT	Task status changed from SUBMITTED to APPROVED by Hrithik Choudhary (GC0008).	Hrithik Choudhary	GC0008	Operations	Executive	STATUS_CHANGE	{"action": "STATUS_CHANGE", "old_status": "SUBMITTED", "new_status": "APPROVED", "comment": null}	\N	2026-10-10 02:53:22.853771+05:30	\N
0b1f05d7-5496-4595-980c-f69374fff101	c3f09177-7fc9-436b-bdd5-d177c419d38e	0438f197-65cc-4fb2-8667-bdaceee1db81	COMMENT	haa ji paaji	Deepak Kumar	GC0005	Operations	Senior Executive	\N	\N	c3f09177-7fc9-436b-bdd5-d177c419d38e_1791622785107_lz1cv28	2026-10-10 14:29:45.170322+05:30	OPERATIONS
f98ca140-9eb9-4f3c-b612-59e59b93ebdd	78f5dcf1-214e-4075-8501-fb05af2d7bd8	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Task reassigned from Hrithik Choudhary (GC0008) to Deepak Kumar (GC0005) by Super Admin (GC0001). Reason: fhdrh	Super Admin	GC0001	Administration	Director	REASSIGNMENT	{"action": "TASK_REASSIGNED", "previous_assignee_id": "65b43201-4875-4caa-a601-b0b535019b48", "previous_assignee_name": "Hrithik Choudhary", "new_assignee_id": "0438f197-65cc-4fb2-8667-bdaceee1db81", "new_assignee_name": "Deepak Kumar", "new_assignee_code": "GC0005", "reason": "fhdrh"}	\N	2026-10-10 18:23:56.579824+05:30	\N
7154b8cd-3b17-4635-8c54-c15b669e36d4	a8c86af8-353e-45ad-be11-10187e517cf7	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0020' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-24 22:55:03.214409+05:30	\N
ef7dac80-9922-4f02-8f78-c16ebf2202e1	ce006ca7-42c0-4b87-85bc-bd92fe729ffb	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0021' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-24 22:56:52.756781+05:30	\N
940efbab-a80b-455a-a53b-7c3a2fd880ff	216eccee-dfbb-48f0-8a63-217ba2b167eb	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0022' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-24 22:59:12.869192+05:30	\N
e3cf5693-5985-462e-96b0-8bf146144531	b7dc6d32-f9ea-4222-adf2-f68aa48f16f1	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0023' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-25 22:19:21.606159+05:30	\N
383073f0-8cca-4b9f-9566-53e8874714e1	249e834e-1cd7-45b5-8707-f78e0ccea2a3	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0024' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-25 22:19:21.671225+05:30	\N
ff8abd52-e6e0-42e1-a52a-0a64f129c1ee	36311f50-9a3c-4203-a79f-6b59eb66a8dc	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0025' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-25 22:19:21.689015+05:30	\N
9ed5ccc3-9eee-4711-8cfa-13fff07f60c2	1f859330-e63f-40f4-ba79-abf2d3714b28	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0026' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-25 22:19:21.717474+05:30	\N
5be35829-1889-484f-a168-36d7a8842d67	3b514f9b-87f3-410d-b475-da6c8d41d9f7	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0027' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-25 22:19:21.750756+05:30	\N
6490d432-2c8d-49a8-9581-4250171d4499	c59e5da3-5272-46c4-8f1f-7810b7647c8c	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0028' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-25 23:04:54.405026+05:30	\N
90995bbc-a275-4c64-bf5c-57b666a4f122	df7f3086-b111-4174-97a6-3f0d5966a2c3	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0029' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-25 23:37:35.760523+05:30	\N
c7037b00-a7a9-4196-945a-10f70cd5a326	98c27bf9-6ba5-4db2-a536-842ed7aad7e4	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0030' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-25 23:37:35.803022+05:30	\N
75072c62-5a47-44e0-a901-9c2c69d1ce0e	082cc2aa-0177-42ae-b670-03e815776e28	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0031' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-25 23:37:35.822343+05:30	\N
5868dcc0-2e51-4a7b-9b11-d94459c55178	c70382c1-9155-480c-b725-a4a10ba56020	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0032' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-25 23:37:35.841892+05:30	\N
8e440134-b4e8-4531-b033-22cfce13ad8d	4af7b6bf-3ff9-41b8-bb28-5cbc588eb07f	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0033' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-25 23:37:35.86555+05:30	\N
cb8533da-f595-44f3-b4eb-e52ff77bc0bf	e50488bf-3e95-449e-ac02-2af61871b164	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0034' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-25 23:48:24.484026+05:30	\N
2fdd763e-a24e-4a18-bb15-f225b02a5cbc	be4a1a11-c14b-40cf-9032-835e278465d2	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0035' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-26 00:08:10.155718+05:30	\N
0aadd278-2687-4d5e-8cbe-f8dc3547546b	49573950-2950-4bd2-9b3f-8b0b72781f51	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0036' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-26 00:08:10.204686+05:30	\N
d906bb5d-0fd9-473f-86a6-a85bab80fa16	d2fee853-0b72-4c9f-94eb-09c7022a2364	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0037' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-26 00:08:10.226672+05:30	\N
ff8b914f-3ab2-4d0e-a05b-2c7bc05699c3	990fefe7-5e97-43d2-a8fb-071848f09bc2	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0038' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-26 00:08:10.249106+05:30	\N
17c3cf04-23c1-4f66-aaca-d53dbdb971fe	3580eeaa-4a41-478a-b9bf-750d201462ba	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0039' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-10-26 00:08:10.276566+05:30	\N
fc953f6a-3237-453e-897c-b28a36170b58	d2fee853-0b72-4c9f-94eb-09c7022a2364	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Task status changed from ASSIGNED to IN_PROGRESS by Super Admin Super Admin (GC0001). Note: Status changed from ASSIGNED to IN_PROGRESS	Super Admin	GC0001	Administration	Director	STATUS_CHANGE	{"action": "STATUS_CHANGE", "old_status": "ASSIGNED", "new_status": "IN_PROGRESS", "comment": "Status changed from ASSIGNED to IN_PROGRESS", "is_override": false}	\N	2026-10-26 00:37:28.043619+05:30	\N
4c04651f-b444-49de-bcdd-48a0b8817c48	d2fee853-0b72-4c9f-94eb-09c7022a2364	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Task status changed from IN_PROGRESS to SUBMITTED by Super Admin Super Admin (GC0001). Note: Status changed from IN_PROGRESS to SUBMITTED	Super Admin	GC0001	Administration	Director	STATUS_CHANGE	{"action": "STATUS_CHANGE", "old_status": "IN_PROGRESS", "new_status": "SUBMITTED", "comment": "Status changed from IN_PROGRESS to SUBMITTED", "is_override": false}	\N	2026-10-26 00:37:29.337175+05:30	\N
b5e59fa7-ab0f-4051-8cb6-3bdcc2aba813	d2fee853-0b72-4c9f-94eb-09c7022a2364	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Task status changed from SUBMITTED to APPROVED by Super Admin Super Admin (GC0001). Note: Status changed from SUBMITTED to APPROVED	Super Admin	GC0001	Administration	Director	STATUS_CHANGE	{"action": "STATUS_CHANGE", "old_status": "SUBMITTED", "new_status": "APPROVED", "comment": "Status changed from SUBMITTED to APPROVED", "is_override": false}	\N	2026-10-26 00:37:30.804914+05:30	\N
58d45502-301a-4509-b0d9-2caeba579566	e4862b88-2c44-4601-8233-f8afcdd5497d	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0040' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-11-01 18:41:07.574263+05:30	\N
9eb9e72f-d464-4242-913e-70b8ea6491c7	654e9028-c1d1-43eb-bdb8-d2f8e36a0f31	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0041' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-11-01 18:42:14.777592+05:30	\N
b8877241-89ec-438f-a0c8-19b7e81fdfb2	4acc34dd-67f3-4afa-945f-134a4fa396fa	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0042' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-11-01 18:42:14.810223+05:30	\N
eb63a9f6-cd74-439a-8d64-af80025237d3	ec94c66a-343d-44b8-a8a5-c864ee8947c1	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0043' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-11-01 18:42:14.834967+05:30	\N
89062783-ad8b-4137-a8c3-ccf0610e531a	3bedc686-8f48-45f1-b760-fbe97941f44c	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0044' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-11-01 18:42:14.855958+05:30	\N
4e6991c9-18d2-4767-a30a-c52ce9404195	266c12f0-57ad-40ea-a62e-6c199c2e5290	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Order 'SO-2026-0045' confirmed and assigned to Mansi Singhal (GC0003) by Super Admin.	Super Admin	GC0001	Administration	Director	ASSIGNMENT_CHANGE	{"action": "ORDER_CONFIRMED", "assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "assignee_name": "Mansi Singhal", "assignee_code": "GC0003"}	\N	2026-11-01 18:42:14.875774+05:30	\N
f7aa4765-a6cf-494d-81db-44b429a5189f	266c12f0-57ad-40ea-a62e-6c199c2e5290	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Task reassigned from Mansi Singhal (GC0003) to Hrithik Choudhary (GC0008) by Super Admin (GC0001). Reason: xcvfds	Super Admin	GC0001	Administration	Director	REASSIGNMENT	{"action": "TASK_REASSIGNED", "previous_assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "previous_assignee_name": "Mansi Singhal", "new_assignee_id": "65b43201-4875-4caa-a601-b0b535019b48", "new_assignee_name": "Hrithik Choudhary", "new_assignee_code": "GC0008", "reason": "xcvfds"}	\N	2026-11-02 18:36:14.450267+05:30	\N
96dab4b5-950e-46dc-81cf-d7b9ffc96b06	e4862b88-2c44-4601-8233-f8afcdd5497d	de526836-5e73-49d7-9be3-8ad07caa6090	SYSTEM_EVENT	Task reassigned from Mansi Singhal (GC0003) to Deepak Kumar (GC0005) by Super Admin (GC0001). Reason: asdfa	Super Admin	GC0001	Administration	Director	REASSIGNMENT	{"action": "TASK_REASSIGNED", "previous_assignee_id": "84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d", "previous_assignee_name": "Mansi Singhal", "new_assignee_id": "0438f197-65cc-4fb2-8667-bdaceee1db81", "new_assignee_name": "Deepak Kumar", "new_assignee_code": "GC0005", "reason": "asdfa"}	\N	2026-11-02 18:36:38.2648+05:30	\N
\.


--
-- Data for Name: task_conversation_read_state; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.task_conversation_read_state (read_id, message_id, user_id, sales_order_id, read_at) FROM stdin;
4272d719-38e6-4271-be49-0a94b688e6a6	fdfdf6af-b4d4-48cc-9842-a53936d30ac9	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:34:05.566906+05:30
1b1fd61d-3322-4f21-b22c-6b071081f17d	f2fd363f-ff78-4990-bf87-c86f67e88cba	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:34:05.566906+05:30
e1765892-5694-4cc8-a7ae-85420b8d8832	a80c2df1-c5cd-4e69-ac2b-ff2026e2a900	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:34:05.566906+05:30
cef78a24-5d21-4e19-9a43-f669cdc92b24	a7baea7c-6b13-41c4-8ae8-b5922a00a9b1	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:34:05.566906+05:30
e602c182-efb0-4c9b-ad85-eba754f52818	2d3a5649-207f-4924-b896-6b0416e95f4f	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:34:05.566906+05:30
439fb48c-7e6c-4799-bdb4-96e2228faf56	7d4b85a1-9e86-4d73-b914-ada45de8a35f	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:34:05.566906+05:30
0796d96f-6294-4276-b303-f1b8551d9d67	a7baea7c-6b13-41c4-8ae8-b5922a00a9b1	de526836-5e73-49d7-9be3-8ad07caa6090	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:39:22.082515+05:30
5c1e6825-77bf-4630-b933-ddd100fa0bb0	2d3a5649-207f-4924-b896-6b0416e95f4f	de526836-5e73-49d7-9be3-8ad07caa6090	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:39:22.082515+05:30
5fa41340-6e35-475b-a49c-9e5816347ebb	26cd87cf-e90f-48f1-93ed-2632fab94f70	de526836-5e73-49d7-9be3-8ad07caa6090	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:39:22.082515+05:30
bd5dfbe3-f077-4781-a95d-240cb68a4a5a	79edcd15-ff81-4a0d-9170-a725881c6bae	de526836-5e73-49d7-9be3-8ad07caa6090	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:39:22.082515+05:30
af1b4972-c74a-48ae-b6ba-168ceec8ca43	d4c0b222-1dff-49d8-a607-e8bbd34e5bf8	de526836-5e73-49d7-9be3-8ad07caa6090	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:39:28.465619+05:30
3cacab2d-0dfc-4d0d-9249-19ed6c755cb2	d4c0b222-1dff-49d8-a607-e8bbd34e5bf8	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:39:32.106369+05:30
767c9013-f013-477b-86cb-c03b7cc8e728	cc177bc6-181a-463d-b533-194e0c606e9b	de526836-5e73-49d7-9be3-8ad07caa6090	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:54:56.270212+05:30
48f00d47-ae77-4e0d-aecc-a80bda240314	cc177bc6-181a-463d-b533-194e0c606e9b	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:55:02.129319+05:30
b5df2054-2493-44a1-8a7b-6a3d851d17cd	5c59378a-01b7-411c-9a22-8f4ebaa95a06	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:55:11.209514+05:30
08530ced-4f8a-4ecf-be97-7f6a0072da9a	5c59378a-01b7-411c-9a22-8f4ebaa95a06	de526836-5e73-49d7-9be3-8ad07caa6090	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-09 13:55:13.907223+05:30
80497c70-a183-439e-917e-e4c6f7e2b0e7	3b719dcb-f8fd-4232-86de-b2a278784788	de526836-5e73-49d7-9be3-8ad07caa6090	e78da1c9-8d92-4e76-bc36-700770eecaab	2026-10-09 13:55:32.769987+05:30
413e2e31-4171-450e-960e-1a92b33878c4	3b719dcb-f8fd-4232-86de-b2a278784788	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	e78da1c9-8d92-4e76-bc36-700770eecaab	2026-10-09 13:55:39.754972+05:30
dfa38e96-5387-445c-ae7d-558aa2b5f66c	099ce54b-0208-4e76-aef5-716d1a340db7	de526836-5e73-49d7-9be3-8ad07caa6090	7558b3f8-00f9-4897-a5b2-5d01f137555c	2026-10-09 15:42:15.531404+05:30
876135f7-2299-4ce7-baab-f8da8384d0e2	45fd985a-b112-40a7-8b4b-983d46f91008	de526836-5e73-49d7-9be3-8ad07caa6090	ce897913-8de9-422d-8d1f-f415cf3504a7	2026-10-09 19:03:35.685795+05:30
eee82b6b-216e-41af-9538-39d3c46177e3	f876e62d-99d2-48a3-be3c-0fefdafde55e	de526836-5e73-49d7-9be3-8ad07caa6090	ce897913-8de9-422d-8d1f-f415cf3504a7	2026-10-09 19:19:17.922373+05:30
3065c0ba-5f8b-4b05-a5d6-419896f44e08	e3dcc3d4-9983-4777-9d6a-3092c4e3bc71	de526836-5e73-49d7-9be3-8ad07caa6090	ce897913-8de9-422d-8d1f-f415cf3504a7	2026-10-09 19:19:26.029788+05:30
3097625d-eb3d-477c-8850-69191c297239	180bbdcb-9834-4644-95cf-569ac940d175	de526836-5e73-49d7-9be3-8ad07caa6090	ce897913-8de9-422d-8d1f-f415cf3504a7	2026-10-09 19:21:57.479945+05:30
143262f8-9f68-494c-bcfe-2ca7e2bbeba0	d4202383-4bbd-4e33-b2ec-c142603b8b38	de526836-5e73-49d7-9be3-8ad07caa6090	a408e780-d55a-4137-a4a2-b8a90bd1bc29	2026-10-09 19:27:56.248847+05:30
149de6e2-f4a4-495a-a330-7dc5c76d2437	ed97dba1-2950-4ca0-99cd-af1b90b666ad	de526836-5e73-49d7-9be3-8ad07caa6090	ce897913-8de9-422d-8d1f-f415cf3504a7	2026-10-09 19:34:33.962955+05:30
c8514d27-0e27-40d3-a0c9-98644f0d02b2	45fd985a-b112-40a7-8b4b-983d46f91008	69984504-68fe-470a-9240-4a37edf511b8	ce897913-8de9-422d-8d1f-f415cf3504a7	2026-10-10 01:54:51.450531+05:30
eda6b804-82fd-4f4c-8461-7eec65bea322	f876e62d-99d2-48a3-be3c-0fefdafde55e	69984504-68fe-470a-9240-4a37edf511b8	ce897913-8de9-422d-8d1f-f415cf3504a7	2026-10-10 01:54:51.450531+05:30
b388b453-a707-41d7-89d7-98add97fca58	e3dcc3d4-9983-4777-9d6a-3092c4e3bc71	69984504-68fe-470a-9240-4a37edf511b8	ce897913-8de9-422d-8d1f-f415cf3504a7	2026-10-10 01:54:51.450531+05:30
3715a32a-1e47-49bd-a602-babc8d7916ac	180bbdcb-9834-4644-95cf-569ac940d175	69984504-68fe-470a-9240-4a37edf511b8	ce897913-8de9-422d-8d1f-f415cf3504a7	2026-10-10 01:54:51.450531+05:30
f5ed12c5-ceb2-40da-b1e7-c8bca459e6f3	ed97dba1-2950-4ca0-99cd-af1b90b666ad	69984504-68fe-470a-9240-4a37edf511b8	ce897913-8de9-422d-8d1f-f415cf3504a7	2026-10-10 01:54:51.450531+05:30
0df0ca86-5544-43eb-80ce-d25bd62da3bb	3b719dcb-f8fd-4232-86de-b2a278784788	69984504-68fe-470a-9240-4a37edf511b8	e78da1c9-8d92-4e76-bc36-700770eecaab	2026-10-10 01:55:00.683219+05:30
68cf41df-c533-4df0-9c56-1c3cba3fdf2b	fdfdf6af-b4d4-48cc-9842-a53936d30ac9	69984504-68fe-470a-9240-4a37edf511b8	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 01:55:09.172422+05:30
21a98c40-df4d-4ec0-be3d-423d999e035e	f2fd363f-ff78-4990-bf87-c86f67e88cba	69984504-68fe-470a-9240-4a37edf511b8	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 01:55:09.172422+05:30
5252aeed-8171-4e27-813a-8b5150f39580	a80c2df1-c5cd-4e69-ac2b-ff2026e2a900	69984504-68fe-470a-9240-4a37edf511b8	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 01:55:09.172422+05:30
3d241326-5d3d-4dee-a820-177284c8ff4e	a7baea7c-6b13-41c4-8ae8-b5922a00a9b1	69984504-68fe-470a-9240-4a37edf511b8	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 01:55:09.172422+05:30
299034b2-4f79-4a23-915c-ea2b1f218b93	2d3a5649-207f-4924-b896-6b0416e95f4f	69984504-68fe-470a-9240-4a37edf511b8	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 01:55:09.172422+05:30
c6ed5b50-cd2d-4175-bb13-5cc20cb2cd94	7d4b85a1-9e86-4d73-b914-ada45de8a35f	69984504-68fe-470a-9240-4a37edf511b8	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 01:55:09.172422+05:30
237e08ac-4e90-4268-bc6e-309b4705d3a8	26cd87cf-e90f-48f1-93ed-2632fab94f70	69984504-68fe-470a-9240-4a37edf511b8	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 01:55:09.172422+05:30
bb85bdcc-2554-487d-98ae-1bffe757413b	79edcd15-ff81-4a0d-9170-a725881c6bae	69984504-68fe-470a-9240-4a37edf511b8	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 01:55:09.172422+05:30
e748de70-8659-443a-a604-23f4d8600d31	d4c0b222-1dff-49d8-a607-e8bbd34e5bf8	69984504-68fe-470a-9240-4a37edf511b8	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 01:55:09.172422+05:30
24dd33f6-8fe4-4312-9262-31af8a8e4212	cc177bc6-181a-463d-b533-194e0c606e9b	69984504-68fe-470a-9240-4a37edf511b8	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 01:55:09.172422+05:30
3d784eef-72bb-4e5c-99d5-6ce01653074d	5c59378a-01b7-411c-9a22-8f4ebaa95a06	69984504-68fe-470a-9240-4a37edf511b8	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 01:55:09.172422+05:30
445d0cc7-26ca-406d-ae50-e82638ea8c99	099ce54b-0208-4e76-aef5-716d1a340db7	69984504-68fe-470a-9240-4a37edf511b8	7558b3f8-00f9-4897-a5b2-5d01f137555c	2026-10-10 01:55:32.844676+05:30
33373f1d-5f51-4733-a52f-720b6db82365	168f3c22-3abb-42e9-bdbd-7a5d27ee652f	8554d145-bdd4-4ee6-b821-74b73cfe40bf	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:44:56.472408+05:30
20f553de-dd21-42ad-9a55-04a90462fd96	84555100-a7ac-4f26-9b8b-7abf4c7d2b58	8554d145-bdd4-4ee6-b821-74b73cfe40bf	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:44:56.482069+05:30
7f325842-1861-4429-9be0-e467d7e14705	5c536fb5-0501-4113-9e7f-8ffd65508f28	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:51:37.01459+05:30
717ce386-cdae-4229-a86e-464b2fce3d8d	f0e42b93-7aac-43af-8128-e3019ed3e179	65b43201-4875-4caa-a601-b0b535019b48	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:04.333608+05:30
96ef4586-2808-45dd-bf1a-d4ef6fcc58b0	6aa9a9cf-6480-435f-affd-2f589d76ebad	65b43201-4875-4caa-a601-b0b535019b48	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:17.242599+05:30
783b4f90-214f-455b-b39d-69978b2dbb72	82fec869-8143-4880-880e-67cb6b0c61e5	65b43201-4875-4caa-a601-b0b535019b48	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:20.323383+05:30
23f73ff6-3550-4b93-a17f-28b15dad6fe8	03ef8bb0-6bfb-4d87-b6e2-cb8c036a4313	65b43201-4875-4caa-a601-b0b535019b48	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:22.853771+05:30
b22cbaf2-54e5-46df-878d-1264b4c79c2d	168f3c22-3abb-42e9-bdbd-7a5d27ee652f	de526836-5e73-49d7-9be3-8ad07caa6090	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:57.338284+05:30
38032666-953d-409c-92f5-cea9ce0c38cf	84555100-a7ac-4f26-9b8b-7abf4c7d2b58	de526836-5e73-49d7-9be3-8ad07caa6090	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:57.338284+05:30
1164e77b-f35f-42f8-b4e0-c6b1de47b430	5c536fb5-0501-4113-9e7f-8ffd65508f28	de526836-5e73-49d7-9be3-8ad07caa6090	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:57.338284+05:30
096b4ad0-df87-4a9c-9e0f-52ca1008d646	283cab07-3b8d-4c32-953c-acc6bcd70408	de526836-5e73-49d7-9be3-8ad07caa6090	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:57.338284+05:30
1ab99b4b-ff77-4d8b-a254-1a8500bd799e	f0e42b93-7aac-43af-8128-e3019ed3e179	de526836-5e73-49d7-9be3-8ad07caa6090	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:57.338284+05:30
667a9624-d57e-41da-918d-9e80d2ba23d2	6aa9a9cf-6480-435f-affd-2f589d76ebad	de526836-5e73-49d7-9be3-8ad07caa6090	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:57.338284+05:30
69a90ec9-4330-4ee5-8c9c-cd45e870ad3f	cdcbe77f-7c89-48cd-b954-81501a2b0ea4	de526836-5e73-49d7-9be3-8ad07caa6090	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:57.338284+05:30
cab2a08f-a5c1-456c-9d27-e9bffdf2853b	82fec869-8143-4880-880e-67cb6b0c61e5	de526836-5e73-49d7-9be3-8ad07caa6090	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:57.338284+05:30
3879cf7e-bd85-44d1-9977-5cf4be56b9b8	03ef8bb0-6bfb-4d87-b6e2-cb8c036a4313	de526836-5e73-49d7-9be3-8ad07caa6090	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 02:53:57.338284+05:30
d4100458-dcf9-4a6e-a476-7ab21a7828da	a80c2df1-c5cd-4e69-ac2b-ff2026e2a900	de526836-5e73-49d7-9be3-8ad07caa6090	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 09:09:52.29418+05:30
cdd56889-2b1a-4130-8013-c5d4367a73ac	f2fd363f-ff78-4990-bf87-c86f67e88cba	de526836-5e73-49d7-9be3-8ad07caa6090	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 09:09:52.29418+05:30
1c014377-69ca-4143-a78b-7190b3f11b3f	7d4b85a1-9e86-4d73-b914-ada45de8a35f	de526836-5e73-49d7-9be3-8ad07caa6090	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 09:09:52.29418+05:30
5503247e-c6e9-4eff-8839-c9fbe5fe0ab0	fdfdf6af-b4d4-48cc-9842-a53936d30ac9	de526836-5e73-49d7-9be3-8ad07caa6090	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 09:09:52.29418+05:30
c806f392-88ef-4ac4-971f-2ee7f0acb772	fdfdf6af-b4d4-48cc-9842-a53936d30ac9	0438f197-65cc-4fb2-8667-bdaceee1db81	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 14:29:33.779358+05:30
653a1715-41d1-447a-8868-c4ac41a7027e	f2fd363f-ff78-4990-bf87-c86f67e88cba	0438f197-65cc-4fb2-8667-bdaceee1db81	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 14:29:33.779358+05:30
b40e9c72-4adc-4faf-a3d1-1c037f6faa30	a80c2df1-c5cd-4e69-ac2b-ff2026e2a900	0438f197-65cc-4fb2-8667-bdaceee1db81	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 14:29:33.779358+05:30
e20a01ac-ca27-448f-86ac-718fa9ed9bb3	7d4b85a1-9e86-4d73-b914-ada45de8a35f	0438f197-65cc-4fb2-8667-bdaceee1db81	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 14:29:33.779358+05:30
4ec6624a-8ec2-41da-a694-b2c67c78e166	26cd87cf-e90f-48f1-93ed-2632fab94f70	0438f197-65cc-4fb2-8667-bdaceee1db81	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 14:29:33.779358+05:30
05e67025-0b62-49e1-b20c-81c7c57b50f3	79edcd15-ff81-4a0d-9170-a725881c6bae	0438f197-65cc-4fb2-8667-bdaceee1db81	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 14:29:33.779358+05:30
04836a4a-2954-43d2-9f57-ef41392acbeb	d4c0b222-1dff-49d8-a607-e8bbd34e5bf8	0438f197-65cc-4fb2-8667-bdaceee1db81	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 14:29:33.779358+05:30
49eb9d4a-8aef-433e-bdf9-1e5a8458001b	cc177bc6-181a-463d-b533-194e0c606e9b	0438f197-65cc-4fb2-8667-bdaceee1db81	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 14:29:33.779358+05:30
efbc2794-19a6-402d-9232-ea94db9b1fbd	5c59378a-01b7-411c-9a22-8f4ebaa95a06	0438f197-65cc-4fb2-8667-bdaceee1db81	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 14:29:33.779358+05:30
3f46e851-c897-42ff-bbc9-78b6c6dfc77b	0b1f05d7-5496-4595-980c-f69374fff101	0438f197-65cc-4fb2-8667-bdaceee1db81	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 14:29:45.170322+05:30
ab893613-92d8-4946-af1a-199ee1f698ff	0b1f05d7-5496-4595-980c-f69374fff101	de526836-5e73-49d7-9be3-8ad07caa6090	c3f09177-7fc9-436b-bdd5-d177c419d38e	2026-10-10 14:29:58.146222+05:30
e8abeb8d-820f-487e-93cc-692d5aefe6d1	f98ca140-9eb9-4f3c-b612-59e59b93ebdd	de526836-5e73-49d7-9be3-8ad07caa6090	78f5dcf1-214e-4075-8501-fb05af2d7bd8	2026-10-10 18:23:56.579824+05:30
7a58de47-c651-410f-8f9f-bf9b9247454c	7154b8cd-3b17-4635-8c54-c15b669e36d4	de526836-5e73-49d7-9be3-8ad07caa6090	a8c86af8-353e-45ad-be11-10187e517cf7	2026-10-24 22:55:03.214409+05:30
ef1ec577-9a2d-447c-82fd-3dc0031e84db	ef7dac80-9922-4f02-8f78-c16ebf2202e1	de526836-5e73-49d7-9be3-8ad07caa6090	ce006ca7-42c0-4b87-85bc-bd92fe729ffb	2026-10-24 22:56:52.756781+05:30
b039ca66-c227-4b39-8973-3796948f92ec	940efbab-a80b-455a-a53b-7c3a2fd880ff	de526836-5e73-49d7-9be3-8ad07caa6090	216eccee-dfbb-48f0-8a63-217ba2b167eb	2026-10-24 22:59:12.869192+05:30
9f551490-637c-4641-9659-bfd9766d0734	e3cf5693-5985-462e-96b0-8bf146144531	de526836-5e73-49d7-9be3-8ad07caa6090	b7dc6d32-f9ea-4222-adf2-f68aa48f16f1	2026-10-25 22:19:21.606159+05:30
c3c584bd-4d7a-44cb-9d2f-c7ce7d392913	383073f0-8cca-4b9f-9566-53e8874714e1	de526836-5e73-49d7-9be3-8ad07caa6090	249e834e-1cd7-45b5-8707-f78e0ccea2a3	2026-10-25 22:19:21.671225+05:30
e3d446c4-852f-43ac-8fc9-2020a6f796ca	ff8abd52-e6e0-42e1-a52a-0a64f129c1ee	de526836-5e73-49d7-9be3-8ad07caa6090	36311f50-9a3c-4203-a79f-6b59eb66a8dc	2026-10-25 22:19:21.689015+05:30
2fb7bd0c-e793-488d-af7c-6703218b5f64	9ed5ccc3-9eee-4711-8cfa-13fff07f60c2	de526836-5e73-49d7-9be3-8ad07caa6090	1f859330-e63f-40f4-ba79-abf2d3714b28	2026-10-25 22:19:21.717474+05:30
acccea32-0e8c-40f0-92ba-1cb64dd49013	5be35829-1889-484f-a168-36d7a8842d67	de526836-5e73-49d7-9be3-8ad07caa6090	3b514f9b-87f3-410d-b475-da6c8d41d9f7	2026-10-25 22:19:21.750756+05:30
3adec03b-e1ec-4338-b03d-c828d5491c6d	6490d432-2c8d-49a8-9581-4250171d4499	de526836-5e73-49d7-9be3-8ad07caa6090	c59e5da3-5272-46c4-8f1f-7810b7647c8c	2026-10-25 23:04:54.405026+05:30
e84e48a6-40d5-49b9-9b57-06f0ae895aa7	90995bbc-a275-4c64-bf5c-57b666a4f122	de526836-5e73-49d7-9be3-8ad07caa6090	df7f3086-b111-4174-97a6-3f0d5966a2c3	2026-10-25 23:37:35.760523+05:30
4259adcf-c0a2-42d9-97e7-a6c0a44aa44f	c7037b00-a7a9-4196-945a-10f70cd5a326	de526836-5e73-49d7-9be3-8ad07caa6090	98c27bf9-6ba5-4db2-a536-842ed7aad7e4	2026-10-25 23:37:35.803022+05:30
410487e6-d467-496f-8569-b0952dd072eb	75072c62-5a47-44e0-a901-9c2c69d1ce0e	de526836-5e73-49d7-9be3-8ad07caa6090	082cc2aa-0177-42ae-b670-03e815776e28	2026-10-25 23:37:35.822343+05:30
2b8bd373-2fd0-4e91-b700-42b86d2d3e24	5868dcc0-2e51-4a7b-9b11-d94459c55178	de526836-5e73-49d7-9be3-8ad07caa6090	c70382c1-9155-480c-b725-a4a10ba56020	2026-10-25 23:37:35.841892+05:30
4db7dee9-cd64-4f57-97b2-d42361aaceab	8e440134-b4e8-4531-b033-22cfce13ad8d	de526836-5e73-49d7-9be3-8ad07caa6090	4af7b6bf-3ff9-41b8-bb28-5cbc588eb07f	2026-10-25 23:37:35.86555+05:30
7d825dad-66a5-4161-918e-5c1c3af2051e	cb8533da-f595-44f3-b4eb-e52ff77bc0bf	de526836-5e73-49d7-9be3-8ad07caa6090	e50488bf-3e95-449e-ac02-2af61871b164	2026-10-25 23:48:24.484026+05:30
ba836719-3c9f-440b-a21e-caccb39b97e2	2fdd763e-a24e-4a18-bb15-f225b02a5cbc	de526836-5e73-49d7-9be3-8ad07caa6090	be4a1a11-c14b-40cf-9032-835e278465d2	2026-10-26 00:08:10.155718+05:30
4b9540c2-e916-4365-ac18-bac2e4c8ad70	0aadd278-2687-4d5e-8cbe-f8dc3547546b	de526836-5e73-49d7-9be3-8ad07caa6090	49573950-2950-4bd2-9b3f-8b0b72781f51	2026-10-26 00:08:10.204686+05:30
40a5ceea-5c40-4d76-a3fe-c467f80aece8	d906bb5d-0fd9-473f-86a6-a85bab80fa16	de526836-5e73-49d7-9be3-8ad07caa6090	d2fee853-0b72-4c9f-94eb-09c7022a2364	2026-10-26 00:08:10.226672+05:30
7085d046-58ea-48fd-9463-8968a31d18ff	ff8b914f-3ab2-4d0e-a05b-2c7bc05699c3	de526836-5e73-49d7-9be3-8ad07caa6090	990fefe7-5e97-43d2-a8fb-071848f09bc2	2026-10-26 00:08:10.249106+05:30
560bf27f-1443-4d4e-b661-7ddf75979570	17c3cf04-23c1-4f66-aaca-d53dbdb971fe	de526836-5e73-49d7-9be3-8ad07caa6090	3580eeaa-4a41-478a-b9bf-750d201462ba	2026-10-26 00:08:10.276566+05:30
4dd4e38d-df8f-4d9a-9cd3-6f381cba8751	fc953f6a-3237-453e-897c-b28a36170b58	de526836-5e73-49d7-9be3-8ad07caa6090	d2fee853-0b72-4c9f-94eb-09c7022a2364	2026-10-26 00:37:28.043619+05:30
cf777414-0d28-4b75-9fb5-2d40ef37ffd8	4c04651f-b444-49de-bcdd-48a0b8817c48	de526836-5e73-49d7-9be3-8ad07caa6090	d2fee853-0b72-4c9f-94eb-09c7022a2364	2026-10-26 00:37:29.337175+05:30
5dbf5297-e3e3-4e00-ae77-f924c8b8743e	b5e59fa7-ab0f-4051-8cb6-3bdcc2aba813	de526836-5e73-49d7-9be3-8ad07caa6090	d2fee853-0b72-4c9f-94eb-09c7022a2364	2026-10-26 00:37:30.804914+05:30
5cdf542b-350f-4278-ab75-621080faefa7	58d45502-301a-4509-b0d9-2caeba579566	de526836-5e73-49d7-9be3-8ad07caa6090	e4862b88-2c44-4601-8233-f8afcdd5497d	2026-11-01 18:41:07.574263+05:30
22789d5f-ae4a-41ca-8810-3910784140a6	9eb9e72f-d464-4242-913e-70b8ea6491c7	de526836-5e73-49d7-9be3-8ad07caa6090	654e9028-c1d1-43eb-bdb8-d2f8e36a0f31	2026-11-01 18:42:14.777592+05:30
246d8c77-d721-4aa6-99dd-55ab7d4ce1c1	b8877241-89ec-438f-a0c8-19b7e81fdfb2	de526836-5e73-49d7-9be3-8ad07caa6090	4acc34dd-67f3-4afa-945f-134a4fa396fa	2026-11-01 18:42:14.810223+05:30
65ddefe6-6678-48f4-a999-69a3006658d0	eb63a9f6-cd74-439a-8d64-af80025237d3	de526836-5e73-49d7-9be3-8ad07caa6090	ec94c66a-343d-44b8-a8a5-c864ee8947c1	2026-11-01 18:42:14.834967+05:30
6d6c55cc-5c49-45da-934e-ba395d540e57	89062783-ad8b-4137-a8c3-ccf0610e531a	de526836-5e73-49d7-9be3-8ad07caa6090	3bedc686-8f48-45f1-b760-fbe97941f44c	2026-11-01 18:42:14.855958+05:30
1cf566f3-6be2-4d54-86c1-cd5dca316f61	4e6991c9-18d2-4767-a30a-c52ce9404195	de526836-5e73-49d7-9be3-8ad07caa6090	266c12f0-57ad-40ea-a62e-6c199c2e5290	2026-11-01 18:42:14.875774+05:30
17e8184c-e603-4c58-baa1-a370fc5087d8	f7aa4765-a6cf-494d-81db-44b429a5189f	de526836-5e73-49d7-9be3-8ad07caa6090	266c12f0-57ad-40ea-a62e-6c199c2e5290	2026-11-02 18:36:14.450267+05:30
d22000fe-4f3a-479a-b5ff-79bb08eb0451	96dab4b5-950e-46dc-81cf-d7b9ffc96b06	de526836-5e73-49d7-9be3-8ad07caa6090	e4862b88-2c44-4601-8233-f8afcdd5497d	2026-11-02 18:36:38.2648+05:30
\.


--
-- Data for Name: user_master; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.user_master (user_id, employee_code, company_id, department_id, designation_id, manager_user_id, first_name, middle_name, last_name, official_email, personal_email, mobile_number, date_of_joining, employment_type, account_status, created_at, updated_at, password_hash, must_change_password, failed_login_attempts, locked_until, last_login_at, password_changed_at, token_version, credentials_initialized_at, is_hod, is_reporting_manager, primary_location) FROM stdin;
dcdee779-494b-4fe7-afa1-d3b66c784fbb	GC0007	5242338c-3887-56db-b86c-c59deae26654	996d9e8f-777e-5a29-a2fb-6feebbce6c1b	08dff813-b33d-5afc-88f8-a90ae8ee77d4	\N	Abhishek	\N	Kumar	mahtoabhi07@gmail.com	mahtoabhi07@gmail.com	+919031999975	2026-10-09	FULL_TIME	ACTIVE	2026-10-09 18:54:44.837102+05:30	2026-10-10 00:56:55.232667+05:30	$argon2id$v=19$m=65536,t=3,p=4$qZmvn6knWwAzsTKnA35Eng$EhTweRKzts6T1MzTTjIkqYpKM5zcjXyqD494TcqXl+c	t	0	\N	\N	\N	1	2026-10-09 18:54:44.938459+05:30	f	f	\N
fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	GC0004	5242338c-3887-56db-b86c-c59deae26654	2326fd8f-44f5-5b3f-8fbd-d11942c8404e	2477adb3-666c-55d9-81e8-1f925f729d5e	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Karishma	\N	Upadhyay	xyz@gmail.com	\N	+919305566903	2026-09-21	FULL_TIME	ACTIVE	2026-09-21 23:37:28.747624+05:30	2026-10-10 00:56:55.232667+05:30	$argon2id$v=19$m=65536,t=3,p=4$1dq050nOwTElBOj7jalm7g$O9uj7D19Qjuk8dE1VrvzSa/9B1wefjm/rUD22GnZlQE	f	0	\N	2026-10-09 10:51:37.549182+05:30	2026-09-21 23:42:02.798064+05:30	2	2026-09-21 23:37:28.851663+05:30	f	f	\N
4ce61bc1-113e-42e4-a934-c58c9d61e541	GC0006	5242338c-3887-56db-b86c-c59deae26654	4369d882-ba37-4dd6-931c-8d96d6a8e7e4	b15c7681-9eb7-5751-a553-82dcd245b163	\N	Arun	\N	Saini	aa@gmail.com	\N	+919192939495	2026-09-29	FULL_TIME	ACTIVE	2026-09-29 23:34:41.406346+05:30	2026-10-10 00:56:55.232667+05:30	$argon2id$v=19$m=65536,t=3,p=4$NTGv2JvayKNfWZfyz4u1gg$5MYghrg8G94SzISwN+LDSZUhBnBgDrrqY48iZ4ZjtWA	t	0	\N	\N	\N	1	2026-09-29 23:34:41.466269+05:30	f	f	\N
84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	GC0003	5242338c-3887-56db-b86c-c59deae26654	996d9e8f-777e-5a29-a2fb-6feebbce6c1b	df74d857-6fc7-5dc9-b085-667b5eed5e43	69984504-68fe-470a-9240-4a37edf511b8	Mansi	\N	Singhal	hr@gocompliances.com	\N	+917292015452	2026-09-21	FULL_TIME	ACTIVE	2026-09-21 23:33:01.824568+05:30	2026-10-10 00:56:55.232667+05:30	$argon2id$v=19$m=65536,t=3,p=4$LAwrU6Yi37rQSE/LjjziHg$lUVqxH1IsOVS94BbYOrsMjNm26kbJEJ+5K/GOQzK2XI	f	0	\N	2026-09-24 02:45:35.622727+05:30	2026-09-24 01:40:38.445461+05:30	2	2026-09-21 23:33:01.956207+05:30	f	f	\N
ebe13c37-2aa9-4b85-b9b2-aab395fd5f08	EP0002	46deca34-710f-5c79-83ab-939b03bffa22	996d9e8f-777e-5a29-a2fb-6feebbce6c1b	2477adb3-666c-55d9-81e8-1f925f729d5e	8554d145-bdd4-4ee6-b821-74b73cfe40bf	Rohan	\N	Sharma	aab@gmail.com	acv@gmail.com	+919090902134	2026-10-09	FULL_TIME	ACTIVE	2026-10-10 02:38:59.036886+05:30	2026-10-10 02:38:59.036886+05:30	$argon2id$v=19$m=65536,t=3,p=4$APUBLrH6svRNdKz8anSCSA$lCst6xR7/SGYugJ1EhWOTM73Yp5M+L+/mGy8u7uwL3U	t	0	\N	\N	\N	1	2026-10-10 02:38:59.108526+05:30	f	f	\N
8554d145-bdd4-4ee6-b821-74b73cfe40bf	EP0001	46deca34-710f-5c79-83ab-939b03bffa22	2326fd8f-44f5-5b3f-8fbd-d11942c8404e	2477adb3-666c-55d9-81e8-1f925f729d5e	\N	Reeya	\N	Soni	ab@gmail.com	adknalk@gmail.com	+919090909090	2026-10-09	FULL_TIME	ACTIVE	2026-10-10 02:37:47.743198+05:30	2026-10-10 02:40:48.608309+05:30	$argon2id$v=19$m=65536,t=3,p=4$lnozVR/HLlky+PiAyzPdSg$Q6baLnzeUtQ79KueHu6cuJJM7UGuPeMAMp44XzKJN7I	f	0	\N	\N	2026-10-10 02:40:48.717055+05:30	2	2026-10-10 02:37:47.8253+05:30	f	f	\N
65b43201-4875-4caa-a601-b0b535019b48	GC0008	5242338c-3887-56db-b86c-c59deae26654	996d9e8f-777e-5a29-a2fb-6feebbce6c1b	b15c7681-9eb7-5751-a553-82dcd245b163	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Hrithik	\N	Choudhary	abc@gmail.com	axz@gmail.com	+919293949596	2026-10-09	FULL_TIME	ACTIVE	2026-10-10 02:46:31.655795+05:30	2026-10-10 02:47:47.588946+05:30	$argon2id$v=19$m=65536,t=3,p=4$8oeG8eLqGmOLyf5T5JSfhQ$8G9TcpwcFGs9fyVEKW2mfGhY4A74UE7FsaFxW8F1qa0	f	0	\N	\N	2026-10-10 02:47:47.684475+05:30	2	2026-10-10 02:46:31.749013+05:30	f	f	\N
69984504-68fe-470a-9240-4a37edf511b8	GC0002	5242338c-3887-56db-b86c-c59deae26654	a9593c21-af68-5071-9436-ee1f58930c3e	91482014-6f86-54a6-beeb-cce2557dc001	\N	Muskan	\N	Gupta	info@gocompliances.com	\N	+918860223325	2026-09-20	FULL_TIME	ACTIVE	2026-09-21 00:16:52.052702+05:30	2026-10-13 18:12:42.854224+05:30	$argon2id$v=19$m=65536,t=3,p=4$QVxYubQWa7gXzBje2m1lGg$/neRT+ESf04HQ0TnpOR6Xv5vbi1BuqYg8dbbdoAdcXc	f	0	\N	2026-10-10 00:18:22.344595+05:30	2026-10-09 19:15:17.973629+05:30	3	2026-10-09 19:14:00.621763+05:30	f	f	\N
0438f197-65cc-4fb2-8667-bdaceee1db81	GC0005	5242338c-3887-56db-b86c-c59deae26654	996d9e8f-777e-5a29-a2fb-6feebbce6c1b	2477adb3-666c-55d9-81e8-1f925f729d5e	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	Deepak	\N	Kumar	projectsgocompliances@gmail.com	\N	+919899004434	2026-09-21	FULL_TIME	ACTIVE	2026-09-21 23:38:48.066515+05:30	2026-10-10 14:29:18.057963+05:30	$argon2id$v=19$m=65536,t=3,p=4$TJTs1+yqr2Q5ZWRg21Binw$90mVBQhE9iqmraGwHYGESf3O7GdtoPxwLvLVras3lNk	f	0	\N	2026-10-10 14:29:18.06431+05:30	2026-10-10 14:28:59.012932+05:30	5	2026-10-10 14:28:29.762681+05:30	f	f	\N
de526836-5e73-49d7-9be3-8ad07caa6090	GC0001	5242338c-3887-56db-b86c-c59deae26654	a9593c21-af68-5071-9436-ee1f58930c3e	91482014-6f86-54a6-beeb-cce2557dc001	69984504-68fe-470a-9240-4a37edf511b8	Super	\N	Admin	research.rnd.gc@gmail.com	\N	+919031999975	2026-09-20	FULL_TIME	ACTIVE	2026-09-20 21:12:01.621263+05:30	2026-10-31 12:05:45.426556+05:30	$argon2id$v=19$m=65536,t=3,p=4$nxa/SK9Xd3PYd/NFV+93wQ$uP4m/SBYmjWccqic17iJFMYcsdKj9X1nDl9VdroDCcE	f	0	\N	2026-10-31 12:05:45.456511+05:30	2026-09-29 14:30:39.910803+05:30	3	\N	f	f	\N
\.


--
-- Data for Name: user_module_permission; Type: TABLE DATA; Schema: public; Owner: abhishekmahto
--

COPY public.user_module_permission (permission_id, user_id, module_id, can_view, can_create, can_edit, can_delete, can_approve, data_scope, status, granted_by_user_id, granted_at, expires_at, updated_at, can_assign, can_reassign, can_export) FROM stdin;
fca0ebae-1198-4876-88e9-4fd3a1dd8d26	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	b7487e39-c3e8-57a2-a5e6-634c985b3c83	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-09-22 01:13:42.12397+05:30	f	f	f
1b050dfa-9339-48c8-b430-9020e0474a1c	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	e70ce939-97de-5e44-b115-b41fa6d47363	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-09-22 01:13:42.12397+05:30	f	f	f
fad88179-f424-482e-8388-1e020eaa7c66	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	d2ceb235-eb43-5ddb-9a49-b54af44240e0	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-09-22 01:13:42.12397+05:30	f	f	f
127e11f6-8c3c-41cf-afa4-a8812fb30a7e	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	3329b014-3cd7-5a33-b75e-948b15c56214	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-09-22 01:13:42.12397+05:30	f	f	f
b287cfe7-f967-438d-8b53-fd791ba363c8	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	f42007df-0de6-5461-9c79-98e63bf52adb	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-09-22 01:13:42.12397+05:30	f	f	f
7eb93357-39e6-417e-bbd7-8ccb89d46ee5	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	f9435bbf-e040-5269-9fe0-5e32b8e2b13b	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-09-22 01:13:42.12397+05:30	f	f	t
b0a42eb2-bc91-4450-bfaf-1f75bf8c2bcd	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	52c75db6-dd49-599c-9d77-6ff9754dfc48	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-09-22 01:13:42.12397+05:30	f	f	f
77738162-8b8b-4942-ac56-f4cd813755bc	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	e8f9e9e9-1017-5b99-adb7-e655f580e389	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-22 01:14:12.279937+05:30	f	f	t
6218a9ba-dd96-4f2c-ad20-fab087b0bb9b	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	e8f9e9e9-1017-5b99-adb7-e655f580e389	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
0938dc6e-0635-4a9f-8b3a-81b537ab12c5	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	71bffc3c-37bb-57f7-b975-1da25326cbcb	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-10-10 01:34:06.437002+05:30	t	f	f
fddcd78d-c199-404c-8282-7ce5c034c052	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	7bcabdee-d53e-5e40-8856-6f40fa5311f3	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-22 01:14:12.279937+05:30	f	f	f
5effacb5-bc47-42c4-825c-ed8ac43e93d7	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	f11ebb42-4525-5cea-8f79-13eee46218eb	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-10-10 01:34:06.437002+05:30	t	t	f
ba9a0d1e-a32f-49d8-b376-dd29bbbc6ec7	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	8ffea6ea-ffd6-5ad7-b660-2df3251af322	t	f	t	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
4298688b-1641-418e-bda8-c9f4c4ca5893	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	94302e7c-5d07-5fe3-87d6-0abbddd54017	t	f	t	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-10-10 01:34:06.437002+05:30	t	t	f
07eecfd4-7462-40cb-ac57-82d73f855350	de526836-5e73-49d7-9be3-8ad07caa6090	41c4500a-3674-5bf4-8af2-bf448d16146d	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-20 21:12:01.621263+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
6b85a80a-abd6-4b19-a063-16444e8e34fa	0438f197-65cc-4fb2-8667-bdaceee1db81	e8f9e9e9-1017-5b99-adb7-e655f580e389	t	f	f	f	f	SELF	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
d3a4470b-daee-48b3-b8ac-06647ad5068e	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	b7487e39-c3e8-57a2-a5e6-634c985b3c83	t	t	t	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-24 02:48:14.347045+05:30	f	f	f
3e330ba4-2ff3-438e-933a-3820c77bfe92	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	1b93187c-a974-50d1-a88f-e06395b01275	t	t	t	t	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
1df46101-6684-4aff-884c-8ec1a8251969	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	d2ceb235-eb43-5ddb-9a49-b54af44240e0	t	f	t	t	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-24 02:48:51.232854+05:30	f	f	t
c7b2515a-b18d-4147-a6d5-1acdc11b0ca2	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	3329b014-3cd7-5a33-b75e-948b15c56214	t	t	t	t	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-24 02:48:51.232854+05:30	f	f	f
5cedd6fe-bc7e-4b91-958d-56b02c7f853f	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	f42007df-0de6-5461-9c79-98e63bf52adb	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-24 02:48:51.232854+05:30	f	f	t
d5d0aae9-518c-4b0f-9cd6-2356bccc1304	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	e70ce939-97de-5e44-b115-b41fa6d47363	t	f	t	t	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-26 01:22:58.087638+05:30	f	f	t
b9e14958-c987-4bca-9c89-92be6360b3fb	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	030bc1e3-dc38-5a1f-a821-16cba85210d7	t	f	t	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
9e4ef0e8-e549-4421-9c42-b46e2ddebb7b	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	856c9fc2-7524-579b-8142-d9f21fb3681f	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	t
2ac26e87-e199-4b9d-870c-c7dc773d9388	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	7bcabdee-d53e-5e40-8856-6f40fa5311f3	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:13:42.12397+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
7cca416c-60d9-45bb-a9aa-6c51ad3dc0bc	0438f197-65cc-4fb2-8667-bdaceee1db81	7bcabdee-d53e-5e40-8856-6f40fa5311f3	t	f	f	f	f	SELF	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
171fcefb-71a9-4566-b983-a17468075980	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	f9435bbf-e040-5269-9fe0-5e32b8e2b13b	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-25 11:09:21.345694+05:30	f	f	f
408d1908-f8b1-4265-a473-3b729456ac73	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	71bffc3c-37bb-57f7-b975-1da25326cbcb	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-25 11:09:21.345694+05:30	f	f	f
3a964340-134c-4fc2-a6f0-41a9ed7ea0c0	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	f11ebb42-4525-5cea-8f79-13eee46218eb	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-25 11:09:21.345694+05:30	f	f	f
bc376054-6af7-43c9-81b4-f1f56f350b98	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	8ffea6ea-ffd6-5ad7-b660-2df3251af322	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-25 11:09:21.345694+05:30	f	f	f
c37cc3c1-33ab-42b8-b010-bc0ef3e5f70a	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	94302e7c-5d07-5fe3-87d6-0abbddd54017	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-25 11:09:21.345694+05:30	f	f	f
642d9d8f-b895-482b-a73e-239c711d159f	0438f197-65cc-4fb2-8667-bdaceee1db81	52c75db6-dd49-599c-9d77-6ff9754dfc48	f	f	f	f	f	SELF	INACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
06989164-071c-4a13-b19e-99ea8fdada74	0438f197-65cc-4fb2-8667-bdaceee1db81	856c9fc2-7524-579b-8142-d9f21fb3681f	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
21f8b5db-b736-4fd5-97e6-878714bd5454	0438f197-65cc-4fb2-8667-bdaceee1db81	94302e7c-5d07-5fe3-87d6-0abbddd54017	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
2c2008fd-b0a5-42a9-85b9-29a96e6495b5	0438f197-65cc-4fb2-8667-bdaceee1db81	8ffea6ea-ffd6-5ad7-b660-2df3251af322	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
2e267a0c-64f0-4e45-886b-bc224257c515	0438f197-65cc-4fb2-8667-bdaceee1db81	3329b014-3cd7-5a33-b75e-948b15c56214	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
408c1772-4583-407e-8b5c-70c2740e97f2	0438f197-65cc-4fb2-8667-bdaceee1db81	f9435bbf-e040-5269-9fe0-5e32b8e2b13b	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
537486d0-9296-4c09-b50d-4a4a91ca2933	0438f197-65cc-4fb2-8667-bdaceee1db81	71bffc3c-37bb-57f7-b975-1da25326cbcb	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
2238f70c-ba38-4524-99af-5a41f960bcaf	69984504-68fe-470a-9240-4a37edf511b8	e8f9e9e9-1017-5b99-adb7-e655f580e389	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
6e5ee794-71ac-4484-be72-d41d2252e9db	69984504-68fe-470a-9240-4a37edf511b8	15984459-38bc-5557-9eb5-ace2fa47e3ab	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 01:17:11.362826+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
aaed6dae-e2e5-455f-a288-10729e0af1cc	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	52c75db6-dd49-599c-9d77-6ff9754dfc48	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-25 11:09:21.345694+05:30	f	f	f
f0d832b8-e53e-4eba-8a43-ebbd6db1dd6a	69984504-68fe-470a-9240-4a37edf511b8	e70ce939-97de-5e44-b115-b41fa6d47363	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
84c29161-6b42-492e-b4da-84d938d35a54	69984504-68fe-470a-9240-4a37edf511b8	869264e8-2cfa-572d-b81c-2a292a4e996b	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 01:17:11.362826+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
ba588f89-d2de-4f2c-b48b-39ea85705337	69984504-68fe-470a-9240-4a37edf511b8	d2ceb235-eb43-5ddb-9a49-b54af44240e0	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
668a8f2f-e138-4725-ae62-83052ce762c9	69984504-68fe-470a-9240-4a37edf511b8	10b7bad6-1d95-5592-baa0-6e4fcbefa35f	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 01:17:11.362826+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
6da27791-91fa-4627-8955-364e6c074764	69984504-68fe-470a-9240-4a37edf511b8	3329b014-3cd7-5a33-b75e-948b15c56214	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
596d4a0a-13ab-427a-b4b0-27a5ee6d57d2	69984504-68fe-470a-9240-4a37edf511b8	7bcabdee-d53e-5e40-8856-6f40fa5311f3	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
0aa08f99-eeb0-4bc6-abdf-c2287ce1a636	de526836-5e73-49d7-9be3-8ad07caa6090	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-20 21:12:01.621263+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
1027566b-fb1e-42d7-867e-632839ab1209	de526836-5e73-49d7-9be3-8ad07caa6090	f9435bbf-e040-5269-9fe0-5e32b8e2b13b	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
1207cc7b-ecd3-4098-b046-81cceda390b1	de526836-5e73-49d7-9be3-8ad07caa6090	b7487e39-c3e8-57a2-a5e6-634c985b3c83	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
134d107d-2072-46f6-8a7b-cc677415b724	de526836-5e73-49d7-9be3-8ad07caa6090	15984459-38bc-5557-9eb5-ace2fa47e3ab	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-20 21:12:01.621263+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
182e0183-faff-4769-828f-aac9ef79ed06	de526836-5e73-49d7-9be3-8ad07caa6090	3329b014-3cd7-5a33-b75e-948b15c56214	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
31b4c089-c986-4146-926b-106e535afb8c	de526836-5e73-49d7-9be3-8ad07caa6090	e70ce939-97de-5e44-b115-b41fa6d47363	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
393d855e-154a-48c0-b83f-32f3d5726a19	de526836-5e73-49d7-9be3-8ad07caa6090	856c9fc2-7524-579b-8142-d9f21fb3681f	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
5073f1c3-76b2-49c8-bbb6-e98c29916dcb	de526836-5e73-49d7-9be3-8ad07caa6090	030bc1e3-dc38-5a1f-a821-16cba85210d7	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
6280b0f1-dcee-4a73-8470-4bdf787cd193	de526836-5e73-49d7-9be3-8ad07caa6090	52c75db6-dd49-599c-9d77-6ff9754dfc48	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-20 21:12:01.621263+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
6c045815-1141-4b29-86c7-33b0fba1cd8b	de526836-5e73-49d7-9be3-8ad07caa6090	71bffc3c-37bb-57f7-b975-1da25326cbcb	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
6e5a2f36-0e83-4302-928d-ffb3429f8e44	de526836-5e73-49d7-9be3-8ad07caa6090	8ffea6ea-ffd6-5ad7-b660-2df3251af322	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
82fcfa61-ed8e-4a18-8f54-b47faf09ab83	de526836-5e73-49d7-9be3-8ad07caa6090	d2ceb235-eb43-5ddb-9a49-b54af44240e0	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
8ce4b6b2-d2ec-4e8b-b8b5-9f245c9007db	de526836-5e73-49d7-9be3-8ad07caa6090	1b93187c-a974-50d1-a88f-e06395b01275	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
99930d7c-4a29-447b-a15f-3517932e5a4c	de526836-5e73-49d7-9be3-8ad07caa6090	f42007df-0de6-5461-9c79-98e63bf52adb	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
c0a8e83c-ce96-438b-9241-04787d1b133a	de526836-5e73-49d7-9be3-8ad07caa6090	94302e7c-5d07-5fe3-87d6-0abbddd54017	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
d6d3acb1-ecba-4566-827a-77df9d793bad	de526836-5e73-49d7-9be3-8ad07caa6090	e8f9e9e9-1017-5b99-adb7-e655f580e389	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
d7a348ef-6dfc-4b03-aeeb-d4f805318427	de526836-5e73-49d7-9be3-8ad07caa6090	f11ebb42-4525-5cea-8f79-13eee46218eb	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-23 01:46:57.682563+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
e7f98212-5aa0-474e-a5a8-4304c1a760d0	de526836-5e73-49d7-9be3-8ad07caa6090	869264e8-2cfa-572d-b81c-2a292a4e996b	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-20 21:12:01.621263+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
e9e9a6ba-04b3-4cd2-a75a-fb7e7c8150de	de526836-5e73-49d7-9be3-8ad07caa6090	7bcabdee-d53e-5e40-8856-6f40fa5311f3	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-20 21:12:01.621263+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
ea31f598-24c0-4ef0-a8db-a0000a2373ac	de526836-5e73-49d7-9be3-8ad07caa6090	fb6844ad-c156-5899-b55e-c55b99e3c81d	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-20 21:12:01.621263+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
f590fcfb-5319-4cf3-8157-eb4e73e1fc11	de526836-5e73-49d7-9be3-8ad07caa6090	10b7bad6-1d95-5592-baa0-6e4fcbefa35f	t	t	t	t	t	ALL	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-20 21:12:01.621263+05:30	\N	2026-09-23 02:04:42.810658+05:30	f	f	t
a31b83bc-bbe7-4434-aa8a-48cb5a72f8d4	69984504-68fe-470a-9240-4a37edf511b8	41c4500a-3674-5bf4-8af2-bf448d16146d	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 01:17:11.362826+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
090fdd60-bcb3-4232-b1da-f57ff5de0e3a	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	1b93187c-a974-50d1-a88f-e06395b01275	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-25 11:09:21.345694+05:30	f	f	f
8906a71f-b29b-4729-9b04-2756ee429119	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	030bc1e3-dc38-5a1f-a821-16cba85210d7	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-25 11:09:21.345694+05:30	f	f	f
01024a43-8c9c-4dc7-9194-b73dbf187b6f	fd90d8ae-e679-4a5e-9a0b-b5d290cffd9b	856c9fc2-7524-579b-8142-d9f21fb3681f	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 01:14:12.279937+05:30	\N	2026-09-25 11:09:21.345694+05:30	f	f	f
92c9326b-3d57-49d4-8b0b-c43e9bcfdab6	69984504-68fe-470a-9240-4a37edf511b8	b7487e39-c3e8-57a2-a5e6-634c985b3c83	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
66f3edbc-5ab9-41f1-9904-7c7ac254401c	69984504-68fe-470a-9240-4a37edf511b8	dc80c923-8a29-5793-95de-70b3cd46fcad	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
e5764e7a-a8dc-4dfd-828a-3c64e799a44f	69984504-68fe-470a-9240-4a37edf511b8	52c75db6-dd49-599c-9d77-6ff9754dfc48	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
e193bb1f-8f3d-41a0-a981-16b1d522a150	69984504-68fe-470a-9240-4a37edf511b8	fb6844ad-c156-5899-b55e-c55b99e3c81d	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 01:17:11.362826+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
0e592144-90ba-45f8-a4db-7522eb23648e	69984504-68fe-470a-9240-4a37edf511b8	ffb8d9dd-e029-5d89-a423-f0c0dee70949	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 01:17:11.362826+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
b65b87ab-446f-4baf-a700-ce1e080a8421	69984504-68fe-470a-9240-4a37edf511b8	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 01:17:11.362826+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
5326088b-7438-46fc-879c-de518725717f	69984504-68fe-470a-9240-4a37edf511b8	4f96f9ef-2722-5327-b54a-638b195dc78d	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
fe808af6-a92c-403d-a593-dcb3e56be8b6	69984504-68fe-470a-9240-4a37edf511b8	c1cf3c01-2902-5d9d-b824-7514a43b7e04	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
58eba507-76f6-4086-83c1-7892d70feaa6	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	4f96f9ef-2722-5327-b54a-638b195dc78d	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 01:34:06.437002+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
f0fb04c9-e2e2-4ed1-8469-765dbbd508b2	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	c1cf3c01-2902-5d9d-b824-7514a43b7e04	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 01:34:06.437002+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
87e437f5-0ffd-49ff-a976-9cb72c66d347	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	10b7bad6-1d95-5592-baa0-6e4fcbefa35f	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 01:34:06.437002+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
bd39bb0a-447e-4236-ba5d-eb2cdb6dc566	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	fb6844ad-c156-5899-b55e-c55b99e3c81d	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 01:34:06.437002+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
ef56640e-00a4-4197-be00-c1a06bdaa782	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	15984459-38bc-5557-9eb5-ace2fa47e3ab	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 01:34:06.437002+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
1e0edd0e-b428-498d-859a-385dfc2b9ded	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	41c4500a-3674-5bf4-8af2-bf448d16146d	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 01:34:06.437002+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
2924294b-3764-407c-b0f6-7739cfa0705f	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	869264e8-2cfa-572d-b81c-2a292a4e996b	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 01:34:06.437002+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
e6907b73-dd7d-45f5-8f2b-3ceaef480480	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	ffb8d9dd-e029-5d89-a423-f0c0dee70949	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 01:34:06.437002+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
4347b135-0a7f-4fc4-85a3-d456cda8f770	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	f	f	f	f	f	COMPANY	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 01:34:06.437002+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
f4c773be-330e-451f-b14c-5b217e425a4f	84ed1dd3-a6e5-4fe6-8212-8a21cd56ac5d	dc80c923-8a29-5793-95de-70b3cd46fcad	f	f	f	f	f	COMPANY	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 01:34:06.437002+05:30	\N	2026-10-10 01:34:06.437002+05:30	f	f	f
b9a46fca-7f25-4e7f-9dd6-a11beec5ea5b	8554d145-bdd4-4ee6-b821-74b73cfe40bf	e8f9e9e9-1017-5b99-adb7-e655f580e389	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	t
dd0a3388-03ce-43bc-9510-9afa447c22b7	8554d145-bdd4-4ee6-b821-74b73cfe40bf	b7487e39-c3e8-57a2-a5e6-634c985b3c83	t	t	t	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
5d0496f4-bffa-4a16-b90b-0fca002319a9	8554d145-bdd4-4ee6-b821-74b73cfe40bf	e70ce939-97de-5e44-b115-b41fa6d47363	t	f	t	t	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	t
d9a0698f-66ba-44fe-886c-a23ee8db5da0	8554d145-bdd4-4ee6-b821-74b73cfe40bf	d2ceb235-eb43-5ddb-9a49-b54af44240e0	t	f	t	t	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	t
6be53d42-86ed-4a27-9b72-a612b0c341c2	8554d145-bdd4-4ee6-b821-74b73cfe40bf	3329b014-3cd7-5a33-b75e-948b15c56214	t	t	t	t	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
7fd18ca1-5638-4a20-a2ad-bffe8d519d11	8554d145-bdd4-4ee6-b821-74b73cfe40bf	f42007df-0de6-5461-9c79-98e63bf52adb	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	t
a7393ecc-0efc-4d3d-aebb-06af9cf95772	8554d145-bdd4-4ee6-b821-74b73cfe40bf	f9435bbf-e040-5269-9fe0-5e32b8e2b13b	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
6d2adeb9-1eda-435d-afc1-3134cb2c7449	8554d145-bdd4-4ee6-b821-74b73cfe40bf	71bffc3c-37bb-57f7-b975-1da25326cbcb	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
6e637d70-046c-43fb-b219-8c54c014ce0f	8554d145-bdd4-4ee6-b821-74b73cfe40bf	f11ebb42-4525-5cea-8f79-13eee46218eb	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
7f3a7672-a902-4e5c-a879-ab94cb915910	8554d145-bdd4-4ee6-b821-74b73cfe40bf	8ffea6ea-ffd6-5ad7-b660-2df3251af322	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
66636845-93c3-40a4-a4a7-2deac2eff5fc	8554d145-bdd4-4ee6-b821-74b73cfe40bf	94302e7c-5d07-5fe3-87d6-0abbddd54017	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
7cd46369-9e47-4f00-9361-60637e5b9d31	8554d145-bdd4-4ee6-b821-74b73cfe40bf	1b93187c-a974-50d1-a88f-e06395b01275	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
d8f76ba3-e6ec-496c-90fb-3c9b3064dc08	8554d145-bdd4-4ee6-b821-74b73cfe40bf	030bc1e3-dc38-5a1f-a821-16cba85210d7	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
198091ac-4f84-4729-9810-cf5b9485d889	8554d145-bdd4-4ee6-b821-74b73cfe40bf	856c9fc2-7524-579b-8142-d9f21fb3681f	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
0aff61ec-97eb-43f9-9e1d-b1eade6d6d70	8554d145-bdd4-4ee6-b821-74b73cfe40bf	4f96f9ef-2722-5327-b54a-638b195dc78d	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
bc8589f2-18a0-419f-9657-d82ecf8bf0a4	8554d145-bdd4-4ee6-b821-74b73cfe40bf	c1cf3c01-2902-5d9d-b824-7514a43b7e04	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
97ac440d-0e76-41b3-9442-ceb956d16417	8554d145-bdd4-4ee6-b821-74b73cfe40bf	10b7bad6-1d95-5592-baa0-6e4fcbefa35f	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
7d8af6db-28ec-41ab-b29f-2c741eccb4e5	8554d145-bdd4-4ee6-b821-74b73cfe40bf	fb6844ad-c156-5899-b55e-c55b99e3c81d	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
d7d0e10e-1831-4b9b-a7a5-d99c27ab576e	8554d145-bdd4-4ee6-b821-74b73cfe40bf	15984459-38bc-5557-9eb5-ace2fa47e3ab	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
ae12a9be-d5fe-4373-bf2f-57b53e2e092d	8554d145-bdd4-4ee6-b821-74b73cfe40bf	41c4500a-3674-5bf4-8af2-bf448d16146d	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
56de78db-1043-499d-8f69-36993105d458	8554d145-bdd4-4ee6-b821-74b73cfe40bf	869264e8-2cfa-572d-b81c-2a292a4e996b	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
8aa232a1-10ef-4dd8-b1c1-8283179b57b1	8554d145-bdd4-4ee6-b821-74b73cfe40bf	ffb8d9dd-e029-5d89-a423-f0c0dee70949	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
7c5aa216-fc8b-46ce-a1e0-53f4ac32ef2f	8554d145-bdd4-4ee6-b821-74b73cfe40bf	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	f	f	f	f	f	COMPANY	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
e11bf1f0-c56d-4c38-bcc2-d85e21317654	8554d145-bdd4-4ee6-b821-74b73cfe40bf	7bcabdee-d53e-5e40-8856-6f40fa5311f3	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
2b837d0f-71f8-453f-af5a-248903c703c8	8554d145-bdd4-4ee6-b821-74b73cfe40bf	52c75db6-dd49-599c-9d77-6ff9754dfc48	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
ea4d6be0-1a74-460f-8001-7ed90449cf20	8554d145-bdd4-4ee6-b821-74b73cfe40bf	dc80c923-8a29-5793-95de-70b3cd46fcad	f	f	f	f	f	COMPANY	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:39:20.352723+05:30	\N	2026-10-10 02:39:20.352723+05:30	f	f	f
95efdd62-8c29-409f-a182-a18d480921ae	65b43201-4875-4caa-a601-b0b535019b48	e8f9e9e9-1017-5b99-adb7-e655f580e389	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
f301d3b0-8647-43e4-9bbe-4e6159992edd	65b43201-4875-4caa-a601-b0b535019b48	b7487e39-c3e8-57a2-a5e6-634c985b3c83	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
d290c8b9-ab5c-4007-9a36-2478c4927905	65b43201-4875-4caa-a601-b0b535019b48	e70ce939-97de-5e44-b115-b41fa6d47363	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
746c17fe-711e-4da9-a4d2-7e401b28fb5c	65b43201-4875-4caa-a601-b0b535019b48	d2ceb235-eb43-5ddb-9a49-b54af44240e0	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
13fda931-58cf-47de-ac79-8b6c2ad13943	65b43201-4875-4caa-a601-b0b535019b48	3329b014-3cd7-5a33-b75e-948b15c56214	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
0202f422-8835-451b-a4ba-01e98ca72662	65b43201-4875-4caa-a601-b0b535019b48	f42007df-0de6-5461-9c79-98e63bf52adb	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
d777df59-33d3-4f84-92ef-44c988c4f5cd	65b43201-4875-4caa-a601-b0b535019b48	f9435bbf-e040-5269-9fe0-5e32b8e2b13b	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	t
8fc9e9d1-3a18-4cd2-b101-a5713dbd83e1	65b43201-4875-4caa-a601-b0b535019b48	71bffc3c-37bb-57f7-b975-1da25326cbcb	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	t	f	f
bd3efa54-29a3-478a-ba28-df1c4d7bbca4	65b43201-4875-4caa-a601-b0b535019b48	f11ebb42-4525-5cea-8f79-13eee46218eb	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	t	t	f
560a2297-410d-48b5-8e8f-33ad7d3511bc	65b43201-4875-4caa-a601-b0b535019b48	8ffea6ea-ffd6-5ad7-b660-2df3251af322	t	f	t	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
23bef6ad-d226-416d-bd56-4d0c8f0d17d4	65b43201-4875-4caa-a601-b0b535019b48	94302e7c-5d07-5fe3-87d6-0abbddd54017	t	f	t	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	t	t	f
c55b4194-b7fb-4cca-9726-6ba3078a7ca1	65b43201-4875-4caa-a601-b0b535019b48	1b93187c-a974-50d1-a88f-e06395b01275	t	t	t	t	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
3af0bc73-190e-4950-91e4-38250edfb22c	65b43201-4875-4caa-a601-b0b535019b48	030bc1e3-dc38-5a1f-a821-16cba85210d7	t	f	t	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
7848abac-e436-45fe-8a6c-276d9bd9b341	65b43201-4875-4caa-a601-b0b535019b48	856c9fc2-7524-579b-8142-d9f21fb3681f	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	t
0b9f71a7-3218-476e-8813-d4e02bd03972	65b43201-4875-4caa-a601-b0b535019b48	4f96f9ef-2722-5327-b54a-638b195dc78d	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
71dfe4c5-9809-4b68-890c-49b3f58b2158	65b43201-4875-4caa-a601-b0b535019b48	c1cf3c01-2902-5d9d-b824-7514a43b7e04	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
d677c71c-7bfb-438d-9f7c-c98892ed4f09	65b43201-4875-4caa-a601-b0b535019b48	10b7bad6-1d95-5592-baa0-6e4fcbefa35f	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
6834c24e-b5a7-4efd-8407-6a7ea60c99f0	65b43201-4875-4caa-a601-b0b535019b48	fb6844ad-c156-5899-b55e-c55b99e3c81d	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
fe041e67-53d8-4f7f-90f0-b1a9aaed59c5	65b43201-4875-4caa-a601-b0b535019b48	15984459-38bc-5557-9eb5-ace2fa47e3ab	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
6f1e6261-0c13-4926-8f7b-8072dffb010c	65b43201-4875-4caa-a601-b0b535019b48	41c4500a-3674-5bf4-8af2-bf448d16146d	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
57d1eaab-dce2-44a4-a7b3-b0d6f935c258	65b43201-4875-4caa-a601-b0b535019b48	869264e8-2cfa-572d-b81c-2a292a4e996b	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
7bd07049-164f-465b-ba2b-978e8b465d95	65b43201-4875-4caa-a601-b0b535019b48	ffb8d9dd-e029-5d89-a423-f0c0dee70949	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
ddd9533e-8adf-4b5f-8675-bcc11c03d2d8	65b43201-4875-4caa-a601-b0b535019b48	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	f	f	f	f	f	COMPANY	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
935563d2-c9e9-480a-951b-42047fca57da	65b43201-4875-4caa-a601-b0b535019b48	7bcabdee-d53e-5e40-8856-6f40fa5311f3	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
e9101fad-f67e-4f19-b63e-fed03e713cee	65b43201-4875-4caa-a601-b0b535019b48	52c75db6-dd49-599c-9d77-6ff9754dfc48	t	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
50fde973-48cd-4134-ae77-de999a74376c	65b43201-4875-4caa-a601-b0b535019b48	dc80c923-8a29-5793-95de-70b3cd46fcad	f	f	f	f	f	COMPANY	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-10 02:46:57.684835+05:30	\N	2026-10-10 02:46:57.684835+05:30	f	f	f
36df936c-92e3-4058-adc6-b9cfbe9ea6e7	dcdee779-494b-4fe7-afa1-d3b66c784fbb	e8f9e9e9-1017-5b99-adb7-e655f580e389	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
ebeeeac3-554f-4987-84a9-7fc2b62edb0f	dcdee779-494b-4fe7-afa1-d3b66c784fbb	b7487e39-c3e8-57a2-a5e6-634c985b3c83	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
93570082-e48c-44fc-b310-cf0a44a4389a	dcdee779-494b-4fe7-afa1-d3b66c784fbb	e70ce939-97de-5e44-b115-b41fa6d47363	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
7284bd8e-9af8-4160-8134-08e4338ec3b6	dcdee779-494b-4fe7-afa1-d3b66c784fbb	d2ceb235-eb43-5ddb-9a49-b54af44240e0	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
0d082762-ff12-4e55-a3c8-9453dde21791	dcdee779-494b-4fe7-afa1-d3b66c784fbb	3329b014-3cd7-5a33-b75e-948b15c56214	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
e86c4712-9c35-4b7f-ae79-b95c601ffdc1	dcdee779-494b-4fe7-afa1-d3b66c784fbb	f42007df-0de6-5461-9c79-98e63bf52adb	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
f462fac0-cb11-4383-b4af-6103a0cf170e	dcdee779-494b-4fe7-afa1-d3b66c784fbb	f9435bbf-e040-5269-9fe0-5e32b8e2b13b	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
2293019e-c740-4c40-b82e-c4a7eca0e936	dcdee779-494b-4fe7-afa1-d3b66c784fbb	71bffc3c-37bb-57f7-b975-1da25326cbcb	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
1a22d73c-8b0c-449e-9e64-332cc57db550	dcdee779-494b-4fe7-afa1-d3b66c784fbb	f11ebb42-4525-5cea-8f79-13eee46218eb	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
f0a5d782-724a-4061-9261-92752271b068	dcdee779-494b-4fe7-afa1-d3b66c784fbb	8ffea6ea-ffd6-5ad7-b660-2df3251af322	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
cedcc5c9-c7cc-41d4-a2e3-769748ec8c54	dcdee779-494b-4fe7-afa1-d3b66c784fbb	94302e7c-5d07-5fe3-87d6-0abbddd54017	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
e517cd0e-08b2-4d8c-98cc-f32315a17af6	dcdee779-494b-4fe7-afa1-d3b66c784fbb	1b93187c-a974-50d1-a88f-e06395b01275	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
3a0c6200-9ec6-4d0f-abb4-cca387479159	dcdee779-494b-4fe7-afa1-d3b66c784fbb	030bc1e3-dc38-5a1f-a821-16cba85210d7	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
4a79b7df-9caa-4a5e-ba0b-272781c41678	dcdee779-494b-4fe7-afa1-d3b66c784fbb	856c9fc2-7524-579b-8142-d9f21fb3681f	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
2b7423da-a101-4b4d-8f98-7c7162c456aa	dcdee779-494b-4fe7-afa1-d3b66c784fbb	4f96f9ef-2722-5327-b54a-638b195dc78d	t	f	f	f	f	COMPANY	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	t
416f3a63-aaa2-46b6-8a15-6b2652fb5fbd	dcdee779-494b-4fe7-afa1-d3b66c784fbb	c1cf3c01-2902-5d9d-b824-7514a43b7e04	t	f	t	f	f	COMPANY	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	t
b75ebac6-117a-46d4-a764-2c87f30f1515	dcdee779-494b-4fe7-afa1-d3b66c784fbb	10b7bad6-1d95-5592-baa0-6e4fcbefa35f	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
a4cdae71-1f16-4540-a24d-31d245fe1925	dcdee779-494b-4fe7-afa1-d3b66c784fbb	fb6844ad-c156-5899-b55e-c55b99e3c81d	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
8f60c50d-88ca-43f7-aa48-8625cf17a383	dcdee779-494b-4fe7-afa1-d3b66c784fbb	15984459-38bc-5557-9eb5-ace2fa47e3ab	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
ab26ee07-30ea-484f-a229-f591fbf955e4	dcdee779-494b-4fe7-afa1-d3b66c784fbb	41c4500a-3674-5bf4-8af2-bf448d16146d	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
419082eb-029e-43cb-8bb6-f51f5fcca264	dcdee779-494b-4fe7-afa1-d3b66c784fbb	869264e8-2cfa-572d-b81c-2a292a4e996b	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
db2baf87-57a1-4366-a273-b9202219efe3	dcdee779-494b-4fe7-afa1-d3b66c784fbb	ffb8d9dd-e029-5d89-a423-f0c0dee70949	f	f	f	f	f	SELF	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
f5cc01c0-a751-4784-997a-309915d2c4f8	dcdee779-494b-4fe7-afa1-d3b66c784fbb	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	f	f	f	f	f	COMPANY	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
2c6a3e65-42c7-4437-84f6-297af0cf9365	dcdee779-494b-4fe7-afa1-d3b66c784fbb	7bcabdee-d53e-5e40-8856-6f40fa5311f3	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
dc739688-b244-4c0f-9ef7-95aeb77ee4b5	dcdee779-494b-4fe7-afa1-d3b66c784fbb	52c75db6-dd49-599c-9d77-6ff9754dfc48	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
61ebc03f-f87a-49a0-8373-3c3a71e3846f	dcdee779-494b-4fe7-afa1-d3b66c784fbb	dc80c923-8a29-5793-95de-70b3cd46fcad	t	f	f	f	f	COMPANY	ACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-10-13 13:37:10.40464+05:30	\N	2026-10-13 13:37:10.40464+05:30	f	f	f
37efe6d7-2cf7-4ea0-a326-6f76d23eecf9	0438f197-65cc-4fb2-8667-bdaceee1db81	58e433d2-4ef4-5e8c-97ef-14b4ea161c00	f	f	f	f	f	SELF	INACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-14 15:52:20.655607+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
eff72d9c-a38e-49dc-ab6d-3e4dff00917e	0438f197-65cc-4fb2-8667-bdaceee1db81	dc80c923-8a29-5793-95de-70b3cd46fcad	f	f	f	f	f	SELF	INACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-14 15:52:20.655607+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
67729751-c16a-4101-a4f1-25a00dcd427c	0438f197-65cc-4fb2-8667-bdaceee1db81	f11ebb42-4525-5cea-8f79-13eee46218eb	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
79f2343a-e59e-4db4-bf65-a8a9a3205d7f	0438f197-65cc-4fb2-8667-bdaceee1db81	1b93187c-a974-50d1-a88f-e06395b01275	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
7e0f0269-2509-418a-9605-c95620ab7b08	0438f197-65cc-4fb2-8667-bdaceee1db81	e70ce939-97de-5e44-b115-b41fa6d47363	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
9140b2c8-63ff-434d-88f7-8777dcd41d8e	0438f197-65cc-4fb2-8667-bdaceee1db81	f42007df-0de6-5461-9c79-98e63bf52adb	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
91f090f9-d759-4f12-b7c6-4b8209b9bc2c	0438f197-65cc-4fb2-8667-bdaceee1db81	d2ceb235-eb43-5ddb-9a49-b54af44240e0	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
b6c458a9-7fc4-4350-b255-3130ff5428f2	0438f197-65cc-4fb2-8667-bdaceee1db81	b7487e39-c3e8-57a2-a5e6-634c985b3c83	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
bbdc7f7b-8e8e-4e65-8e13-790088cbf7a4	0438f197-65cc-4fb2-8667-bdaceee1db81	030bc1e3-dc38-5a1f-a821-16cba85210d7	f	f	f	f	f	SELF	INACTIVE	de526836-5e73-49d7-9be3-8ad07caa6090	2026-09-22 11:29:59.25451+05:30	\N	2026-10-14 15:52:20.655607+05:30	f	f	f
5cbd1964-a980-486a-92cf-52cf0fde14e7	69984504-68fe-470a-9240-4a37edf511b8	f9435bbf-e040-5269-9fe0-5e32b8e2b13b	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
1b7beec1-4ef4-43c7-afc4-011cc20bcda1	69984504-68fe-470a-9240-4a37edf511b8	71bffc3c-37bb-57f7-b975-1da25326cbcb	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
9a7d65c8-1ad7-468a-a99c-95f8a222b5ec	69984504-68fe-470a-9240-4a37edf511b8	78a60b47-6f1b-5b57-9f3f-5ed2699fe304	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-13 18:13:14.378728+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
c8b6eb8e-f6f1-4f0f-bd15-55476597d18b	69984504-68fe-470a-9240-4a37edf511b8	3cd0da8a-3cab-5ef6-9a32-d9a9d93e938c	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-13 18:13:14.378728+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
c7f106a4-398f-4f29-ba87-b6aeddaa60f3	69984504-68fe-470a-9240-4a37edf511b8	f11ebb42-4525-5cea-8f79-13eee46218eb	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
038646ec-224b-4f28-b0f7-f05e6b2df7a7	69984504-68fe-470a-9240-4a37edf511b8	8ffea6ea-ffd6-5ad7-b660-2df3251af322	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
76c7fd4f-1720-46b6-beee-744e8ebb1b65	69984504-68fe-470a-9240-4a37edf511b8	18e769eb-7e9c-53a6-b755-dff18784c20e	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-13 18:13:14.378728+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
2b740e52-6268-4ed3-b66b-d796b7033ca6	69984504-68fe-470a-9240-4a37edf511b8	94302e7c-5d07-5fe3-87d6-0abbddd54017	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
c1647121-d623-46a3-a6ea-7b39829b0654	69984504-68fe-470a-9240-4a37edf511b8	1a151a5c-447f-53a0-b60e-ee8dfb30a74e	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-13 18:13:14.378728+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
a895a2f2-0e24-4014-b384-a053ac83b4b6	69984504-68fe-470a-9240-4a37edf511b8	f42007df-0de6-5461-9c79-98e63bf52adb	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
8172d822-1707-4667-b15d-130330629849	69984504-68fe-470a-9240-4a37edf511b8	1b93187c-a974-50d1-a88f-e06395b01275	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
e43ba758-51e9-4d8f-a928-544af871ccb8	69984504-68fe-470a-9240-4a37edf511b8	c486b814-f422-51a6-ab3b-a28667353323	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-13 18:13:14.378728+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
20fa97a3-2f0b-4810-8dd6-86245a8bb4ea	69984504-68fe-470a-9240-4a37edf511b8	030bc1e3-dc38-5a1f-a821-16cba85210d7	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
1f8b8f3e-84b3-4a03-8b4d-165b9b3f6a19	69984504-68fe-470a-9240-4a37edf511b8	856c9fc2-7524-579b-8142-d9f21fb3681f	t	t	t	f	t	ALL	ACTIVE	69984504-68fe-470a-9240-4a37edf511b8	2026-10-10 00:25:15.456133+05:30	\N	2026-10-14 16:36:57.015478+05:30	f	f	f
\.


--
-- Name: accounts_audit_log accounts_audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_audit_log
    ADD CONSTRAINT accounts_audit_log_pkey PRIMARY KEY (audit_id);


--
-- Name: accounts_expense accounts_expense_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_expense
    ADD CONSTRAINT accounts_expense_pkey PRIMARY KEY (expense_id);


--
-- Name: accounts_follow_up accounts_follow_up_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_follow_up
    ADD CONSTRAINT accounts_follow_up_pkey PRIMARY KEY (follow_up_id);


--
-- Name: accounts_invoice accounts_invoice_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_invoice
    ADD CONSTRAINT accounts_invoice_pkey PRIMARY KEY (invoice_id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: application_activity_log application_activity_log_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.application_activity_log
    ADD CONSTRAINT application_activity_log_pkey PRIMARY KEY (activity_id);


--
-- Name: application_assignment_history application_assignment_history_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.application_assignment_history
    ADD CONSTRAINT application_assignment_history_pkey PRIMARY KEY (history_id);


--
-- Name: application_document application_document_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.application_document
    ADD CONSTRAINT application_document_pkey PRIMARY KEY (app_doc_id);


--
-- Name: auth_refresh_token auth_refresh_token_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.auth_refresh_token
    ADD CONSTRAINT auth_refresh_token_pkey PRIMARY KEY (refresh_token_id);


--
-- Name: client_master client_master_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.client_master
    ADD CONSTRAINT client_master_pkey PRIMARY KEY (client_id);


--
-- Name: company_master company_master_employee_code_prefix_key; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.company_master
    ADD CONSTRAINT company_master_employee_code_prefix_key UNIQUE (employee_code_prefix);


--
-- Name: company_master company_master_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.company_master
    ADD CONSTRAINT company_master_pkey PRIMARY KEY (company_id);


--
-- Name: department_master department_master_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.department_master
    ADD CONSTRAINT department_master_pkey PRIMARY KEY (department_id);


--
-- Name: designation_master designation_master_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.designation_master
    ADD CONSTRAINT designation_master_pkey PRIMARY KEY (designation_id);


--
-- Name: impersonation_audit_logs impersonation_audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.impersonation_audit_logs
    ADD CONSTRAINT impersonation_audit_logs_pkey PRIMARY KEY (audit_id);


--
-- Name: impersonation_sessions impersonation_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.impersonation_sessions
    ADD CONSTRAINT impersonation_sessions_pkey PRIMARY KEY (session_id);


--
-- Name: module_master module_master_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.module_master
    ADD CONSTRAINT module_master_pkey PRIMARY KEY (module_id);


--
-- Name: operation_application operation_application_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operation_application
    ADD CONSTRAINT operation_application_pkey PRIMARY KEY (application_id);


--
-- Name: operation_remark operation_remark_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operation_remark
    ADD CONSTRAINT operation_remark_pkey PRIMARY KEY (remark_id);


--
-- Name: operations_coordinator_config operations_coordinator_config_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operations_coordinator_config
    ADD CONSTRAINT operations_coordinator_config_pkey PRIMARY KEY (config_id);


--
-- Name: payment_transaction payment_transaction_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.payment_transaction
    ADD CONSTRAINT payment_transaction_pkey PRIMARY KEY (payment_id);


--
-- Name: permission_audit_log permission_audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.permission_audit_log
    ADD CONSTRAINT permission_audit_log_pkey PRIMARY KEY (audit_id);


--
-- Name: sales_order_audit_log sales_order_audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.sales_order_audit_log
    ADD CONSTRAINT sales_order_audit_log_pkey PRIMARY KEY (audit_id);


--
-- Name: sales_order sales_order_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.sales_order
    ADD CONSTRAINT sales_order_pkey PRIMARY KEY (order_id);


--
-- Name: service_master service_master_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.service_master
    ADD CONSTRAINT service_master_pkey PRIMARY KEY (service_id);


--
-- Name: service_required_document service_required_document_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.service_required_document
    ADD CONSTRAINT service_required_document_pkey PRIMARY KEY (doc_config_id);


--
-- Name: source_master source_master_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.source_master
    ADD CONSTRAINT source_master_pkey PRIMARY KEY (source_id);


--
-- Name: task_conversation_message task_conversation_message_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.task_conversation_message
    ADD CONSTRAINT task_conversation_message_pkey PRIMARY KEY (message_id);


--
-- Name: task_conversation_read_state task_conversation_read_state_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.task_conversation_read_state
    ADD CONSTRAINT task_conversation_read_state_pkey PRIMARY KEY (read_id);


--
-- Name: accounts_expense uq_accounts_expense_number; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_expense
    ADD CONSTRAINT uq_accounts_expense_number UNIQUE (expense_number);


--
-- Name: accounts_invoice uq_accounts_invoice_company_type_number; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_invoice
    ADD CONSTRAINT uq_accounts_invoice_company_type_number UNIQUE (company_id, invoice_type, invoice_number);


--
-- Name: department_master uq_department_code; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.department_master
    ADD CONSTRAINT uq_department_code UNIQUE (department_code);


--
-- Name: department_master uq_department_name; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.department_master
    ADD CONSTRAINT uq_department_name UNIQUE (department_name);


--
-- Name: designation_master uq_designation_code; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.designation_master
    ADD CONSTRAINT uq_designation_code UNIQUE (designation_code);


--
-- Name: designation_master uq_designation_name; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.designation_master
    ADD CONSTRAINT uq_designation_name UNIQUE (designation_name);


--
-- Name: operation_application uq_op_app_sales_order_id; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operation_application
    ADD CONSTRAINT uq_op_app_sales_order_id UNIQUE (sales_order_id);


--
-- Name: operations_coordinator_config uq_operations_coordinator_company_id; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operations_coordinator_config
    ADD CONSTRAINT uq_operations_coordinator_company_id UNIQUE (company_id);


--
-- Name: payment_transaction uq_payment_transaction_number; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.payment_transaction
    ADD CONSTRAINT uq_payment_transaction_number UNIQUE (payment_number);


--
-- Name: service_required_document uq_service_required_doc_service_code; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.service_required_document
    ADD CONSTRAINT uq_service_required_doc_service_code UNIQUE (service_id, document_code);


--
-- Name: source_master uq_source_code; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.source_master
    ADD CONSTRAINT uq_source_code UNIQUE (source_code);


--
-- Name: source_master uq_source_name; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.source_master
    ADD CONSTRAINT uq_source_name UNIQUE (source_name);


--
-- Name: task_conversation_read_state uq_task_conv_read_user_message; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.task_conversation_read_state
    ADD CONSTRAINT uq_task_conv_read_user_message UNIQUE (user_id, message_id);


--
-- Name: user_module_permission uq_user_module_permission_user_module; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.user_module_permission
    ADD CONSTRAINT uq_user_module_permission_user_module UNIQUE (user_id, module_id);


--
-- Name: user_master user_master_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.user_master
    ADD CONSTRAINT user_master_pkey PRIMARY KEY (user_id);


--
-- Name: user_module_permission user_module_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.user_module_permission
    ADD CONSTRAINT user_module_permission_pkey PRIMARY KEY (permission_id);


--
-- Name: ix_accounts_audit_log_action; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_audit_log_action ON public.accounts_audit_log USING btree (action);


--
-- Name: ix_accounts_audit_log_actor_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_audit_log_actor_user_id ON public.accounts_audit_log USING btree (actor_user_id);


--
-- Name: ix_accounts_audit_log_company_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_audit_log_company_id ON public.accounts_audit_log USING btree (company_id);


--
-- Name: ix_accounts_audit_log_created_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_audit_log_created_at ON public.accounts_audit_log USING btree (created_at);


--
-- Name: ix_accounts_audit_log_entity_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_audit_log_entity_id ON public.accounts_audit_log USING btree (entity_id);


--
-- Name: ix_accounts_audit_log_entity_type; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_audit_log_entity_type ON public.accounts_audit_log USING btree (entity_type);


--
-- Name: ix_accounts_expense_approval_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_expense_approval_status ON public.accounts_expense USING btree (approval_status);


--
-- Name: ix_accounts_expense_category; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_expense_category ON public.accounts_expense USING btree (category);


--
-- Name: ix_accounts_expense_company_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_expense_company_id ON public.accounts_expense USING btree (company_id);


--
-- Name: ix_accounts_expense_created_by_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_expense_created_by_user_id ON public.accounts_expense USING btree (created_by_user_id);


--
-- Name: ix_accounts_expense_expense_date; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_expense_expense_date ON public.accounts_expense USING btree (expense_date);


--
-- Name: ix_accounts_expense_expense_number; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_accounts_expense_expense_number ON public.accounts_expense USING btree (expense_number);


--
-- Name: ix_accounts_expense_paid_by_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_expense_paid_by_user_id ON public.accounts_expense USING btree (paid_by_user_id);


--
-- Name: ix_accounts_expense_sales_order_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_expense_sales_order_id ON public.accounts_expense USING btree (sales_order_id);


--
-- Name: ix_accounts_expense_settlement_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_expense_settlement_status ON public.accounts_expense USING btree (settlement_status);


--
-- Name: ix_accounts_follow_up_company_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_follow_up_company_id ON public.accounts_follow_up USING btree (company_id);


--
-- Name: ix_accounts_follow_up_created_by_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_follow_up_created_by_user_id ON public.accounts_follow_up USING btree (created_by_user_id);


--
-- Name: ix_accounts_follow_up_follow_up_date; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_follow_up_follow_up_date ON public.accounts_follow_up USING btree (follow_up_date);


--
-- Name: ix_accounts_follow_up_next_follow_up_date; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_follow_up_next_follow_up_date ON public.accounts_follow_up USING btree (next_follow_up_date);


--
-- Name: ix_accounts_follow_up_sales_order_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_follow_up_sales_order_id ON public.accounts_follow_up USING btree (sales_order_id);


--
-- Name: ix_accounts_invoice_company_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_invoice_company_id ON public.accounts_invoice USING btree (company_id);


--
-- Name: ix_accounts_invoice_created_by_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_invoice_created_by_user_id ON public.accounts_invoice USING btree (created_by_user_id);


--
-- Name: ix_accounts_invoice_invoice_date; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_invoice_invoice_date ON public.accounts_invoice USING btree (invoice_date);


--
-- Name: ix_accounts_invoice_invoice_number; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_invoice_invoice_number ON public.accounts_invoice USING btree (invoice_number);


--
-- Name: ix_accounts_invoice_invoice_type; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_invoice_invoice_type ON public.accounts_invoice USING btree (invoice_type);


--
-- Name: ix_accounts_invoice_sales_order_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_accounts_invoice_sales_order_id ON public.accounts_invoice USING btree (sales_order_id);


--
-- Name: ix_application_activity_log_action_type; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_application_activity_log_action_type ON public.application_activity_log USING btree (action_type);


--
-- Name: ix_application_activity_log_application_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_application_activity_log_application_id ON public.application_activity_log USING btree (application_id);


--
-- Name: ix_application_activity_log_created_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_application_activity_log_created_at ON public.application_activity_log USING btree (created_at);


--
-- Name: ix_application_assignment_history_application_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_application_assignment_history_application_id ON public.application_assignment_history USING btree (application_id);


--
-- Name: ix_application_document_application_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_application_document_application_id ON public.application_document USING btree (application_id);


--
-- Name: ix_application_document_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_application_document_status ON public.application_document USING btree (status);


--
-- Name: ix_auth_refresh_token_expires_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_auth_refresh_token_expires_at ON public.auth_refresh_token USING btree (expires_at);


--
-- Name: ix_auth_refresh_token_jti; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_auth_refresh_token_jti ON public.auth_refresh_token USING btree (jti);


--
-- Name: ix_auth_refresh_token_revoked_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_auth_refresh_token_revoked_at ON public.auth_refresh_token USING btree (revoked_at);


--
-- Name: ix_auth_refresh_token_token_hash; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_auth_refresh_token_token_hash ON public.auth_refresh_token USING btree (token_hash);


--
-- Name: ix_auth_refresh_token_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_auth_refresh_token_user_id ON public.auth_refresh_token USING btree (user_id);


--
-- Name: ix_client_master_client_name; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_client_master_client_name ON public.client_master USING btree (client_name);


--
-- Name: ix_client_master_company_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_client_master_company_id ON public.client_master USING btree (company_id);


--
-- Name: ix_client_master_created_by_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_client_master_created_by_user_id ON public.client_master USING btree (created_by_user_id);


--
-- Name: ix_client_master_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_client_master_status ON public.client_master USING btree (status);


--
-- Name: ix_company_master_company_code; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_company_master_company_code ON public.company_master USING btree (company_code);


--
-- Name: ix_company_master_company_name; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_company_master_company_name ON public.company_master USING btree (company_name);


--
-- Name: ix_company_master_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_company_master_status ON public.company_master USING btree (status);


--
-- Name: ix_department_master_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_department_master_status ON public.department_master USING btree (status);


--
-- Name: ix_designation_master_level_rank; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_designation_master_level_rank ON public.designation_master USING btree (level_rank);


--
-- Name: ix_designation_master_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_designation_master_status ON public.designation_master USING btree (status);


--
-- Name: ix_imp_audit_actor_created; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_imp_audit_actor_created ON public.impersonation_audit_logs USING btree (actor_admin_id, created_at);


--
-- Name: ix_imp_audit_target_created; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_imp_audit_target_created ON public.impersonation_audit_logs USING btree (target_user_id, created_at);


--
-- Name: ix_impersonation_audit_logs_action; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_audit_logs_action ON public.impersonation_audit_logs USING btree (action);


--
-- Name: ix_impersonation_audit_logs_actor_admin_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_audit_logs_actor_admin_id ON public.impersonation_audit_logs USING btree (actor_admin_id);


--
-- Name: ix_impersonation_audit_logs_created_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_audit_logs_created_at ON public.impersonation_audit_logs USING btree (created_at);


--
-- Name: ix_impersonation_audit_logs_session_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_audit_logs_session_id ON public.impersonation_audit_logs USING btree (session_id);


--
-- Name: ix_impersonation_audit_logs_target_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_audit_logs_target_user_id ON public.impersonation_audit_logs USING btree (target_user_id);


--
-- Name: ix_impersonation_sessions_active_expiry; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_sessions_active_expiry ON public.impersonation_sessions USING btree (is_active, expires_at);


--
-- Name: ix_impersonation_sessions_actor_admin_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_sessions_actor_admin_id ON public.impersonation_sessions USING btree (actor_admin_id);


--
-- Name: ix_impersonation_sessions_admin_target; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_sessions_admin_target ON public.impersonation_sessions USING btree (actor_admin_id, target_user_id);


--
-- Name: ix_impersonation_sessions_created_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_sessions_created_at ON public.impersonation_sessions USING btree (created_at);


--
-- Name: ix_impersonation_sessions_expires_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_sessions_expires_at ON public.impersonation_sessions USING btree (expires_at);


--
-- Name: ix_impersonation_sessions_impersonation_token_jti; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_sessions_impersonation_token_jti ON public.impersonation_sessions USING btree (impersonation_token_jti);


--
-- Name: ix_impersonation_sessions_is_active; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_sessions_is_active ON public.impersonation_sessions USING btree (is_active);


--
-- Name: ix_impersonation_sessions_target_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_impersonation_sessions_target_user_id ON public.impersonation_sessions USING btree (target_user_id);


--
-- Name: ix_module_master_display_order; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_module_master_display_order ON public.module_master USING btree (display_order);


--
-- Name: ix_module_master_module_code; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_module_master_module_code ON public.module_master USING btree (module_code);


--
-- Name: ix_module_master_parent_module_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_module_master_parent_module_id ON public.module_master USING btree (parent_module_id);


--
-- Name: ix_module_master_route; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_module_master_route ON public.module_master USING btree (route);


--
-- Name: ix_module_master_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_module_master_status ON public.module_master USING btree (status);


--
-- Name: ix_op_app_deleted_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_op_app_deleted_at ON public.operation_application USING btree (deleted_at);


--
-- Name: ix_op_app_deleted_by; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_op_app_deleted_by ON public.operation_application USING btree (deleted_by);


--
-- Name: ix_operation_application_application_number; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_operation_application_application_number ON public.operation_application USING btree (application_number);


--
-- Name: ix_operation_application_application_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operation_application_application_status ON public.operation_application USING btree (application_status);


--
-- Name: ix_operation_application_assigned_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operation_application_assigned_at ON public.operation_application USING btree (assigned_at);


--
-- Name: ix_operation_application_assigned_to_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operation_application_assigned_to_user_id ON public.operation_application USING btree (assigned_to_user_id);


--
-- Name: ix_operation_application_client_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operation_application_client_id ON public.operation_application USING btree (client_id);


--
-- Name: ix_operation_application_company_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operation_application_company_id ON public.operation_application USING btree (company_id);


--
-- Name: ix_operation_application_priority; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operation_application_priority ON public.operation_application USING btree (priority);


--
-- Name: ix_operation_application_sales_order_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_operation_application_sales_order_id ON public.operation_application USING btree (sales_order_id);


--
-- Name: ix_operation_application_service_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operation_application_service_id ON public.operation_application USING btree (service_id);


--
-- Name: ix_operation_application_target_due_date; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operation_application_target_due_date ON public.operation_application USING btree (target_due_date);


--
-- Name: ix_operation_remark_application_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operation_remark_application_id ON public.operation_remark USING btree (application_id);


--
-- Name: ix_operation_remark_author_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operation_remark_author_user_id ON public.operation_remark USING btree (author_user_id);


--
-- Name: ix_operation_remark_created_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operation_remark_created_at ON public.operation_remark USING btree (created_at);


--
-- Name: ix_operations_coordinator_config_company_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operations_coordinator_config_company_id ON public.operations_coordinator_config USING btree (company_id);


--
-- Name: ix_operations_coordinator_config_coordinator_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_operations_coordinator_config_coordinator_user_id ON public.operations_coordinator_config USING btree (coordinator_user_id);


--
-- Name: ix_payment_transaction_company_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_payment_transaction_company_id ON public.payment_transaction USING btree (company_id);


--
-- Name: ix_payment_transaction_payment_date; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_payment_transaction_payment_date ON public.payment_transaction USING btree (payment_date);


--
-- Name: ix_payment_transaction_payment_number; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_payment_transaction_payment_number ON public.payment_transaction USING btree (payment_number);


--
-- Name: ix_payment_transaction_sales_order_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_payment_transaction_sales_order_id ON public.payment_transaction USING btree (sales_order_id);


--
-- Name: ix_payment_transaction_submitted_by_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_payment_transaction_submitted_by_user_id ON public.payment_transaction USING btree (submitted_by_user_id);


--
-- Name: ix_payment_transaction_transaction_reference; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_payment_transaction_transaction_reference ON public.payment_transaction USING btree (transaction_reference);


--
-- Name: ix_payment_transaction_verification_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_payment_transaction_verification_status ON public.payment_transaction USING btree (verification_status);


--
-- Name: ix_permission_audit_actor_created; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_permission_audit_actor_created ON public.permission_audit_log USING btree (actor_user_id, created_at);


--
-- Name: ix_permission_audit_log_action_type; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_permission_audit_log_action_type ON public.permission_audit_log USING btree (action_type);


--
-- Name: ix_permission_audit_log_actor_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_permission_audit_log_actor_user_id ON public.permission_audit_log USING btree (actor_user_id);


--
-- Name: ix_permission_audit_log_created_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_permission_audit_log_created_at ON public.permission_audit_log USING btree (created_at);


--
-- Name: ix_permission_audit_log_target_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_permission_audit_log_target_user_id ON public.permission_audit_log USING btree (target_user_id);


--
-- Name: ix_permission_audit_target_created; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_permission_audit_target_created ON public.permission_audit_log USING btree (target_user_id, created_at);


--
-- Name: ix_sales_order_audit_log_action_type; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_audit_log_action_type ON public.sales_order_audit_log USING btree (action_type);


--
-- Name: ix_sales_order_audit_log_actor_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_audit_log_actor_user_id ON public.sales_order_audit_log USING btree (actor_user_id);


--
-- Name: ix_sales_order_audit_log_created_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_audit_log_created_at ON public.sales_order_audit_log USING btree (created_at);


--
-- Name: ix_sales_order_audit_log_linked_task_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_audit_log_linked_task_id ON public.sales_order_audit_log USING btree (linked_task_id);


--
-- Name: ix_sales_order_audit_log_sales_order_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_audit_log_sales_order_id ON public.sales_order_audit_log USING btree (sales_order_id);


--
-- Name: ix_sales_order_client_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_client_id ON public.sales_order USING btree (client_id);


--
-- Name: ix_sales_order_company_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_company_id ON public.sales_order USING btree (company_id);


--
-- Name: ix_sales_order_confirmation_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_confirmation_status ON public.sales_order USING btree (confirmation_status);


--
-- Name: ix_sales_order_confirmed_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_confirmed_at ON public.sales_order USING btree (confirmed_at);


--
-- Name: ix_sales_order_deleted_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_deleted_at ON public.sales_order USING btree (deleted_at);


--
-- Name: ix_sales_order_deleted_by; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_deleted_by ON public.sales_order USING btree (deleted_by);


--
-- Name: ix_sales_order_gst_invoice_required; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_gst_invoice_required ON public.sales_order USING btree (gst_invoice_required);


--
-- Name: ix_sales_order_lead_source; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_lead_source ON public.sales_order USING btree (lead_source);


--
-- Name: ix_sales_order_location; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_location ON public.sales_order USING btree (location);


--
-- Name: ix_sales_order_order_date; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_order_date ON public.sales_order USING btree (order_date);


--
-- Name: ix_sales_order_order_number; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_sales_order_order_number ON public.sales_order USING btree (order_number);


--
-- Name: ix_sales_order_payment_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_payment_status ON public.sales_order USING btree (payment_status);


--
-- Name: ix_sales_order_proforma_invoice_no; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_proforma_invoice_no ON public.sales_order USING btree (proforma_invoice_no);


--
-- Name: ix_sales_order_salesperson_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_salesperson_user_id ON public.sales_order USING btree (salesperson_user_id);


--
-- Name: ix_sales_order_service_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_service_id ON public.sales_order USING btree (service_id);


--
-- Name: ix_sales_order_tax_invoice_no; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_sales_order_tax_invoice_no ON public.sales_order USING btree (tax_invoice_no);


--
-- Name: ix_service_master_category; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_service_master_category ON public.service_master USING btree (category);


--
-- Name: ix_service_master_service_code; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_service_master_service_code ON public.service_master USING btree (service_code);


--
-- Name: ix_service_master_service_name; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_service_master_service_name ON public.service_master USING btree (service_name);


--
-- Name: ix_service_master_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_service_master_status ON public.service_master USING btree (status);


--
-- Name: ix_service_required_document_service_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_service_required_document_service_id ON public.service_required_document USING btree (service_id);


--
-- Name: ix_source_master_source_code; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_source_master_source_code ON public.source_master USING btree (source_code);


--
-- Name: ix_task_conv_msg_order_created; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_task_conv_msg_order_created ON public.task_conversation_message USING btree (sales_order_id, created_at);


--
-- Name: ix_task_conv_msg_order_idempotency; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_task_conv_msg_order_idempotency ON public.task_conversation_message USING btree (sales_order_id, idempotency_key) WHERE (idempotency_key IS NOT NULL);


--
-- Name: ix_task_conv_read_user_order; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_task_conv_read_user_order ON public.task_conversation_read_state USING btree (user_id, sales_order_id);


--
-- Name: ix_task_conv_read_user_time; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_task_conv_read_user_time ON public.task_conversation_read_state USING btree (user_id, read_at);


--
-- Name: ix_task_conversation_message_author_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_task_conversation_message_author_user_id ON public.task_conversation_message USING btree (author_user_id);


--
-- Name: ix_task_conversation_message_created_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_task_conversation_message_created_at ON public.task_conversation_message USING btree (created_at);


--
-- Name: ix_task_conversation_message_event_type; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_task_conversation_message_event_type ON public.task_conversation_message USING btree (event_type);


--
-- Name: ix_task_conversation_message_message_type; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_task_conversation_message_message_type ON public.task_conversation_message USING btree (message_type);


--
-- Name: ix_task_conversation_message_originating_module; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_task_conversation_message_originating_module ON public.task_conversation_message USING btree (originating_module);


--
-- Name: ix_task_conversation_message_sales_order_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_task_conversation_message_sales_order_id ON public.task_conversation_message USING btree (sales_order_id);


--
-- Name: ix_task_conversation_read_state_message_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_task_conversation_read_state_message_id ON public.task_conversation_read_state USING btree (message_id);


--
-- Name: ix_task_conversation_read_state_sales_order_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_task_conversation_read_state_sales_order_id ON public.task_conversation_read_state USING btree (sales_order_id);


--
-- Name: ix_task_conversation_read_state_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_task_conversation_read_state_user_id ON public.task_conversation_read_state USING btree (user_id);


--
-- Name: ix_user_master_account_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_user_master_account_status ON public.user_master USING btree (account_status);


--
-- Name: ix_user_master_company_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_user_master_company_id ON public.user_master USING btree (company_id);


--
-- Name: ix_user_master_department_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_user_master_department_id ON public.user_master USING btree (department_id);


--
-- Name: ix_user_master_designation_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_user_master_designation_id ON public.user_master USING btree (designation_id);


--
-- Name: ix_user_master_employee_code; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_user_master_employee_code ON public.user_master USING btree (employee_code);


--
-- Name: ix_user_master_manager_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_user_master_manager_user_id ON public.user_master USING btree (manager_user_id);


--
-- Name: ix_user_master_official_email_lower; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE UNIQUE INDEX ix_user_master_official_email_lower ON public.user_master USING btree (lower((official_email)::text));


--
-- Name: ix_user_module_permission_expires_at; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_user_module_permission_expires_at ON public.user_module_permission USING btree (expires_at);


--
-- Name: ix_user_module_permission_granted_by_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_user_module_permission_granted_by_user_id ON public.user_module_permission USING btree (granted_by_user_id);


--
-- Name: ix_user_module_permission_module_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_user_module_permission_module_id ON public.user_module_permission USING btree (module_id);


--
-- Name: ix_user_module_permission_status; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_user_module_permission_status ON public.user_module_permission USING btree (status);


--
-- Name: ix_user_module_permission_user_id; Type: INDEX; Schema: public; Owner: abhishekmahto
--

CREATE INDEX ix_user_module_permission_user_id ON public.user_module_permission USING btree (user_id);


--
-- Name: accounts_audit_log fk_accounts_audit_log_actor_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_audit_log
    ADD CONSTRAINT fk_accounts_audit_log_actor_user_id FOREIGN KEY (actor_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: accounts_audit_log fk_accounts_audit_log_company_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_audit_log
    ADD CONSTRAINT fk_accounts_audit_log_company_id FOREIGN KEY (company_id) REFERENCES public.company_master(company_id) ON DELETE RESTRICT;


--
-- Name: accounts_expense fk_accounts_expense_approved_by; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_expense
    ADD CONSTRAINT fk_accounts_expense_approved_by FOREIGN KEY (approved_by_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: accounts_expense fk_accounts_expense_company_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_expense
    ADD CONSTRAINT fk_accounts_expense_company_id FOREIGN KEY (company_id) REFERENCES public.company_master(company_id) ON DELETE RESTRICT;


--
-- Name: accounts_expense fk_accounts_expense_created_by; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_expense
    ADD CONSTRAINT fk_accounts_expense_created_by FOREIGN KEY (created_by_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: accounts_expense fk_accounts_expense_paid_by_user; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_expense
    ADD CONSTRAINT fk_accounts_expense_paid_by_user FOREIGN KEY (paid_by_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: accounts_expense fk_accounts_expense_sales_order_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_expense
    ADD CONSTRAINT fk_accounts_expense_sales_order_id FOREIGN KEY (sales_order_id) REFERENCES public.sales_order(order_id) ON DELETE SET NULL;


--
-- Name: accounts_expense fk_accounts_expense_settled_by; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_expense
    ADD CONSTRAINT fk_accounts_expense_settled_by FOREIGN KEY (settled_by_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: accounts_follow_up fk_accounts_follow_up_company_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_follow_up
    ADD CONSTRAINT fk_accounts_follow_up_company_id FOREIGN KEY (company_id) REFERENCES public.company_master(company_id) ON DELETE RESTRICT;


--
-- Name: accounts_follow_up fk_accounts_follow_up_created_by; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_follow_up
    ADD CONSTRAINT fk_accounts_follow_up_created_by FOREIGN KEY (created_by_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: accounts_follow_up fk_accounts_follow_up_sales_order_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_follow_up
    ADD CONSTRAINT fk_accounts_follow_up_sales_order_id FOREIGN KEY (sales_order_id) REFERENCES public.sales_order(order_id) ON DELETE RESTRICT;


--
-- Name: accounts_invoice fk_accounts_invoice_company_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_invoice
    ADD CONSTRAINT fk_accounts_invoice_company_id FOREIGN KEY (company_id) REFERENCES public.company_master(company_id) ON DELETE RESTRICT;


--
-- Name: accounts_invoice fk_accounts_invoice_created_by; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_invoice
    ADD CONSTRAINT fk_accounts_invoice_created_by FOREIGN KEY (created_by_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: accounts_invoice fk_accounts_invoice_sales_order_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.accounts_invoice
    ADD CONSTRAINT fk_accounts_invoice_sales_order_id FOREIGN KEY (sales_order_id) REFERENCES public.sales_order(order_id) ON DELETE RESTRICT;


--
-- Name: application_activity_log fk_app_activity_actor_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.application_activity_log
    ADD CONSTRAINT fk_app_activity_actor_id FOREIGN KEY (actor_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: application_activity_log fk_app_activity_application_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.application_activity_log
    ADD CONSTRAINT fk_app_activity_application_id FOREIGN KEY (application_id) REFERENCES public.operation_application(application_id) ON DELETE CASCADE;


--
-- Name: application_assignment_history fk_app_assign_hist_app_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.application_assignment_history
    ADD CONSTRAINT fk_app_assign_hist_app_id FOREIGN KEY (application_id) REFERENCES public.operation_application(application_id) ON DELETE CASCADE;


--
-- Name: application_assignment_history fk_app_assign_hist_assigned_by_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.application_assignment_history
    ADD CONSTRAINT fk_app_assign_hist_assigned_by_id FOREIGN KEY (assigned_by_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: application_assignment_history fk_app_assign_hist_new_assignee_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.application_assignment_history
    ADD CONSTRAINT fk_app_assign_hist_new_assignee_id FOREIGN KEY (new_assignee_user_id) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: application_assignment_history fk_app_assign_hist_prev_assignee_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.application_assignment_history
    ADD CONSTRAINT fk_app_assign_hist_prev_assignee_id FOREIGN KEY (previous_assignee_user_id) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: application_document fk_app_doc_application_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.application_document
    ADD CONSTRAINT fk_app_doc_application_id FOREIGN KEY (application_id) REFERENCES public.operation_application(application_id) ON DELETE CASCADE;


--
-- Name: application_document fk_app_doc_verified_by_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.application_document
    ADD CONSTRAINT fk_app_doc_verified_by_id FOREIGN KEY (verified_by_user_id) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: client_master fk_client_company_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.client_master
    ADD CONSTRAINT fk_client_company_id FOREIGN KEY (company_id) REFERENCES public.company_master(company_id) ON DELETE RESTRICT;


--
-- Name: client_master fk_client_created_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.client_master
    ADD CONSTRAINT fk_client_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: impersonation_audit_logs fk_imp_audit_actor_admin_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.impersonation_audit_logs
    ADD CONSTRAINT fk_imp_audit_actor_admin_id FOREIGN KEY (actor_admin_id) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: impersonation_audit_logs fk_imp_audit_session_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.impersonation_audit_logs
    ADD CONSTRAINT fk_imp_audit_session_id FOREIGN KEY (session_id) REFERENCES public.impersonation_sessions(session_id) ON DELETE SET NULL;


--
-- Name: impersonation_audit_logs fk_imp_audit_target_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.impersonation_audit_logs
    ADD CONSTRAINT fk_imp_audit_target_user_id FOREIGN KEY (target_user_id) REFERENCES public.user_master(user_id) ON DELETE CASCADE;


--
-- Name: impersonation_sessions fk_impersonation_actor_admin_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.impersonation_sessions
    ADD CONSTRAINT fk_impersonation_actor_admin_id FOREIGN KEY (actor_admin_id) REFERENCES public.user_master(user_id) ON DELETE CASCADE;


--
-- Name: impersonation_sessions fk_impersonation_target_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.impersonation_sessions
    ADD CONSTRAINT fk_impersonation_target_user_id FOREIGN KEY (target_user_id) REFERENCES public.user_master(user_id) ON DELETE CASCADE;


--
-- Name: module_master fk_module_parent_module_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.module_master
    ADD CONSTRAINT fk_module_parent_module_id FOREIGN KEY (parent_module_id) REFERENCES public.module_master(module_id) ON DELETE RESTRICT;


--
-- Name: operation_application fk_op_app_assigned_by_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operation_application
    ADD CONSTRAINT fk_op_app_assigned_by_id FOREIGN KEY (assigned_by_user_id) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: operation_application fk_op_app_assigned_to_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operation_application
    ADD CONSTRAINT fk_op_app_assigned_to_id FOREIGN KEY (assigned_to_user_id) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: operation_application fk_op_app_client_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operation_application
    ADD CONSTRAINT fk_op_app_client_id FOREIGN KEY (client_id) REFERENCES public.client_master(client_id) ON DELETE RESTRICT;


--
-- Name: operation_application fk_op_app_company_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operation_application
    ADD CONSTRAINT fk_op_app_company_id FOREIGN KEY (company_id) REFERENCES public.company_master(company_id) ON DELETE RESTRICT;


--
-- Name: operation_application fk_op_app_deleted_by; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operation_application
    ADD CONSTRAINT fk_op_app_deleted_by FOREIGN KEY (deleted_by) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: operation_application fk_op_app_sales_order_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operation_application
    ADD CONSTRAINT fk_op_app_sales_order_id FOREIGN KEY (sales_order_id) REFERENCES public.sales_order(order_id) ON DELETE RESTRICT;


--
-- Name: operation_application fk_op_app_service_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operation_application
    ADD CONSTRAINT fk_op_app_service_id FOREIGN KEY (service_id) REFERENCES public.service_master(service_id) ON DELETE RESTRICT;


--
-- Name: operation_remark fk_op_remark_application_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operation_remark
    ADD CONSTRAINT fk_op_remark_application_id FOREIGN KEY (application_id) REFERENCES public.operation_application(application_id) ON DELETE CASCADE;


--
-- Name: operation_remark fk_op_remark_author_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operation_remark
    ADD CONSTRAINT fk_op_remark_author_user_id FOREIGN KEY (author_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: operations_coordinator_config fk_ops_coord_cfg_company_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operations_coordinator_config
    ADD CONSTRAINT fk_ops_coord_cfg_company_id FOREIGN KEY (company_id) REFERENCES public.company_master(company_id) ON DELETE CASCADE;


--
-- Name: operations_coordinator_config fk_ops_coord_cfg_coordinator_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operations_coordinator_config
    ADD CONSTRAINT fk_ops_coord_cfg_coordinator_user_id FOREIGN KEY (coordinator_user_id) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: operations_coordinator_config fk_ops_coord_cfg_updated_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.operations_coordinator_config
    ADD CONSTRAINT fk_ops_coord_cfg_updated_by_user_id FOREIGN KEY (updated_by_user_id) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: payment_transaction fk_payment_transaction_company_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.payment_transaction
    ADD CONSTRAINT fk_payment_transaction_company_id FOREIGN KEY (company_id) REFERENCES public.company_master(company_id) ON DELETE RESTRICT;


--
-- Name: payment_transaction fk_payment_transaction_reversed_by; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.payment_transaction
    ADD CONSTRAINT fk_payment_transaction_reversed_by FOREIGN KEY (reversed_by_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: payment_transaction fk_payment_transaction_sales_order_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.payment_transaction
    ADD CONSTRAINT fk_payment_transaction_sales_order_id FOREIGN KEY (sales_order_id) REFERENCES public.sales_order(order_id) ON DELETE RESTRICT;


--
-- Name: payment_transaction fk_payment_transaction_submitted_by; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.payment_transaction
    ADD CONSTRAINT fk_payment_transaction_submitted_by FOREIGN KEY (submitted_by_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: payment_transaction fk_payment_transaction_verified_by; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.payment_transaction
    ADD CONSTRAINT fk_payment_transaction_verified_by FOREIGN KEY (verified_by_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: permission_audit_log fk_permission_audit_actor_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.permission_audit_log
    ADD CONSTRAINT fk_permission_audit_actor_user_id FOREIGN KEY (actor_user_id) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: permission_audit_log fk_permission_audit_target_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.permission_audit_log
    ADD CONSTRAINT fk_permission_audit_target_user_id FOREIGN KEY (target_user_id) REFERENCES public.user_master(user_id) ON DELETE CASCADE;


--
-- Name: user_module_permission fk_permission_granted_by_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.user_module_permission
    ADD CONSTRAINT fk_permission_granted_by_user_id FOREIGN KEY (granted_by_user_id) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: user_module_permission fk_permission_module_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.user_module_permission
    ADD CONSTRAINT fk_permission_module_id FOREIGN KEY (module_id) REFERENCES public.module_master(module_id) ON DELETE RESTRICT;


--
-- Name: user_module_permission fk_permission_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.user_module_permission
    ADD CONSTRAINT fk_permission_user_id FOREIGN KEY (user_id) REFERENCES public.user_master(user_id) ON DELETE CASCADE;


--
-- Name: auth_refresh_token fk_refresh_token_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.auth_refresh_token
    ADD CONSTRAINT fk_refresh_token_user_id FOREIGN KEY (user_id) REFERENCES public.user_master(user_id) ON DELETE CASCADE;


--
-- Name: sales_order_audit_log fk_sales_order_audit_actor_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.sales_order_audit_log
    ADD CONSTRAINT fk_sales_order_audit_actor_id FOREIGN KEY (actor_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: sales_order_audit_log fk_sales_order_audit_order_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.sales_order_audit_log
    ADD CONSTRAINT fk_sales_order_audit_order_id FOREIGN KEY (sales_order_id) REFERENCES public.sales_order(order_id) ON DELETE CASCADE;


--
-- Name: sales_order fk_sales_order_client_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.sales_order
    ADD CONSTRAINT fk_sales_order_client_id FOREIGN KEY (client_id) REFERENCES public.client_master(client_id) ON DELETE RESTRICT;


--
-- Name: sales_order fk_sales_order_company_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.sales_order
    ADD CONSTRAINT fk_sales_order_company_id FOREIGN KEY (company_id) REFERENCES public.company_master(company_id) ON DELETE RESTRICT;


--
-- Name: sales_order fk_sales_order_deleted_by; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.sales_order
    ADD CONSTRAINT fk_sales_order_deleted_by FOREIGN KEY (deleted_by) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: sales_order fk_sales_order_salesperson_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.sales_order
    ADD CONSTRAINT fk_sales_order_salesperson_id FOREIGN KEY (salesperson_user_id) REFERENCES public.user_master(user_id) ON DELETE RESTRICT;


--
-- Name: sales_order fk_sales_order_service_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.sales_order
    ADD CONSTRAINT fk_sales_order_service_id FOREIGN KEY (service_id) REFERENCES public.service_master(service_id) ON DELETE RESTRICT;


--
-- Name: service_required_document fk_service_required_doc_service_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.service_required_document
    ADD CONSTRAINT fk_service_required_doc_service_id FOREIGN KEY (service_id) REFERENCES public.service_master(service_id) ON DELETE CASCADE;


--
-- Name: task_conversation_message fk_task_conv_msg_author_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.task_conversation_message
    ADD CONSTRAINT fk_task_conv_msg_author_user_id FOREIGN KEY (author_user_id) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- Name: task_conversation_message fk_task_conv_msg_sales_order_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.task_conversation_message
    ADD CONSTRAINT fk_task_conv_msg_sales_order_id FOREIGN KEY (sales_order_id) REFERENCES public.sales_order(order_id) ON DELETE CASCADE;


--
-- Name: task_conversation_read_state fk_task_conv_read_message_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.task_conversation_read_state
    ADD CONSTRAINT fk_task_conv_read_message_id FOREIGN KEY (message_id) REFERENCES public.task_conversation_message(message_id) ON DELETE CASCADE;


--
-- Name: task_conversation_read_state fk_task_conv_read_sales_order_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.task_conversation_read_state
    ADD CONSTRAINT fk_task_conv_read_sales_order_id FOREIGN KEY (sales_order_id) REFERENCES public.sales_order(order_id) ON DELETE CASCADE;


--
-- Name: task_conversation_read_state fk_task_conv_read_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.task_conversation_read_state
    ADD CONSTRAINT fk_task_conv_read_user_id FOREIGN KEY (user_id) REFERENCES public.user_master(user_id) ON DELETE CASCADE;


--
-- Name: user_master fk_user_company_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.user_master
    ADD CONSTRAINT fk_user_company_id FOREIGN KEY (company_id) REFERENCES public.company_master(company_id) ON DELETE RESTRICT;


--
-- Name: user_master fk_user_department_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.user_master
    ADD CONSTRAINT fk_user_department_id FOREIGN KEY (department_id) REFERENCES public.department_master(department_id) ON DELETE RESTRICT;


--
-- Name: user_master fk_user_designation_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.user_master
    ADD CONSTRAINT fk_user_designation_id FOREIGN KEY (designation_id) REFERENCES public.designation_master(designation_id) ON DELETE RESTRICT;


--
-- Name: user_master fk_user_manager_user_id; Type: FK CONSTRAINT; Schema: public; Owner: abhishekmahto
--

ALTER TABLE ONLY public.user_master
    ADD CONSTRAINT fk_user_manager_user_id FOREIGN KEY (manager_user_id) REFERENCES public.user_master(user_id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict tkBFkfoUwUaTXrvUXh0Tdh5KJkQ6AWUzVOFZWEhTah0ztY7D0n2hXLEKvXAACXK

