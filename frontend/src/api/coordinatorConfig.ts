/**
 * API client methods for Admin Operations Coordinator Configuration.
 */
import { apiClient } from './client';
import type {
  CoordinatorConfigUpdatePayload,
  EligibleCoordinatorOption,
  OperationsCoordinatorConfigItem,
} from '../types/coordinatorConfig';

/**
 * List all company Operations coordinator mappings.
 */
export async function getCoordinatorConfigsApi(): Promise<OperationsCoordinatorConfigItem[]> {
  const response = await apiClient.get<OperationsCoordinatorConfigItem[]>('/admin/coordinator-configs');
  return response.data;
}

/**
 * List all active Operations employees eligible to be coordinators.
 */
export async function getEligibleCoordinatorsApi(): Promise<EligibleCoordinatorOption[]> {
  const response = await apiClient.get<EligibleCoordinatorOption[]>('/admin/coordinator-configs/eligible-coordinators');
  return response.data;
}

/**
 * Update or set default Operations coordinator for a company.
 */
export async function updateCoordinatorConfigApi(
  payload: CoordinatorConfigUpdatePayload
): Promise<OperationsCoordinatorConfigItem> {
  const response = await apiClient.put<OperationsCoordinatorConfigItem>('/admin/coordinator-configs', payload);
  return response.data;
}
