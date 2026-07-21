import { apiClient } from "../api_client";

export interface InvoiceItemPayload {
  invoice_number: string;
  debtor_ruc: string;
  debtor_name: string;
  amount: number;
  issue_date: string;
  due_date: string;
}

export interface CreateSheetPayload {
  currency: string;
  invoices: InvoiceItemPayload[];
}

export interface InvoiceSheetDTO {
  id: number;
  sheet_code: string;
  company_id: number;
  currency: string;
  total_amount: number;
  advance_amount: number;
  interest_fee: number;
  commission: number;
  net_disbursement: number;
  advance_rate: number;
  monthly_rate: number;
  status: string;
  created_at?: string;
  invoices_count?: number;
  invoices?: Array<{
    id: number;
    invoice_number: string;
    drawer_ruc: string;
    debtor_ruc: string;
    debtor_name: string;
    amount: number;
    currency: string;
    issue_date: string;
    due_date: string;
    days_to_maturity: number;
    sunat_status: string;
    is_approved: boolean;
    rejection_reason?: string;
  }>;
}

export class SalesAdapter {
  static async createSheet(
    payload: CreateSheetPayload
  ): Promise<{ message: string; sheet: InvoiceSheetDTO }> {
    return apiClient.post<{ message: string; sheet: InvoiceSheetDTO }>(
      "/api/v1/sales/sheets",
      payload
    );
  }

  static async getSheetById(id: number): Promise<{ sheet: InvoiceSheetDTO }> {
    return apiClient.get<{ sheet: InvoiceSheetDTO }>(`/api/v1/sales/sheets/${id}`);
  }

  static async listSheets(): Promise<{ sheets: InvoiceSheetDTO[] }> {
    return apiClient.get<{ sheets: InvoiceSheetDTO[] }>("/api/v1/sales/sheets");
  }
}
