using System.Collections.Generic;
using System.Threading.Tasks;
using FinanceASP.NETCore.Models;

namespace FinanceASP.NETCore.Repositories
{
    public interface IHoldingsRepository
    {
        Task<List<Holdings>> GetHoldings(string userId);
        Task<bool> BuyStock(string userId, string stockName, int quantity);
        Task<bool> SellStock(string userId, string stockName, int quantity);
        Task<bool> LogTransaction(string userId, string stockName, int quantity);
    }
}