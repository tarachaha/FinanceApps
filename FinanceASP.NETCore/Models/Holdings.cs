namespace FinanceASP.NETCore.Models
{
    public class Holdings
    {
        public int HoldingsId { get; set; }
        public User Id { get; set; }
        public string Symbol { get; set; }
        public int Shares { get; set; }

    }
}