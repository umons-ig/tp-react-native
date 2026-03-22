export type Transaction = {
  id: number;
  amount: number;
  description: string;
  category: string;
  type: 'income' | 'expense';
  date: string;
};

export type CategoryTotal = {
  category: string;
  total: number;
};
