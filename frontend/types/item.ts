export interface Item {
  id: number;
  title: string;
  guid: string;
  pub_date: string;
  flag_status: {
    status: string;
  };
}