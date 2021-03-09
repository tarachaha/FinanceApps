using System;

namespace FinanceASP.NETCore.Models
{
    public class Transaction
    {
        public int TransactionId { get; set; }
        public User Id { get; set; }
        public string Symbol { get; set; }
        public DateTime Timestamp { get; set; }
        public double Price { get; set; }
        public int Shares { get; set; }
        public string TypeOfTransaction { get; set; }
    }
}