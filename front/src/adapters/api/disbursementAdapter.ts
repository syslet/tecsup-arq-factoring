import { apiClient } from "../api_client";
import type { InvoiceSheetDTO } from "./salesAdapter";

export interface DisbursementDTO {
  id: number;
  sheet_id: number;
  annotation_code: string;
  amount: number;
  currency: string;
  bank_name: string;
  bank_account_number: string;
  cci: string;
  status: string;
  executed_at?: string;
}

export class DisbursementAdapter {
  static async acceptAndDisburse(
    sheetId: number
  ): Promise<{ message: string; sheet: InvoiceSheetDTO; disbursement: DisbursementDTO }> {
    return apiClient.post<{
      message: string;
      sheet: InvoiceSheetDTO;
      disbursement: DisbursementDTO;
    }>(`/api/v1/sales/sheets/${sheetId}/accept`);
  }

  static async getDisbursementById(id: number): Promise<{ disbursement: DisbursementDTO }> {
    return apiClient.get<{ disbursement: DisbursementDTO }>(`/api/v1/disbursements/${id}`);
  }
}
