using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using FinanceASP.NETCore.Data;
using FinanceASP.NETCore.Models;
using Microsoft.EntityFrameworkCore;

namespace FinanceASP.NETCore.Repositories
{
    public class HoldingsRepository : IHoldingsRepository
    {
        private readonly FinanceDbContext _context;
        private readonly IStockQueryService _stockQuery;

        public HoldingsRepository(FinanceDbContext context, IStockQueryService stockQuery)
        {
            context = _context;
            stockQuery = _stockQuery;
        }
        public Task<bool> BuyStock(string userId, string stockName, int quantity)
        {
            throw new NotImplementedException();
        }

        public async Task<List<Holdings>> GetHoldings(string userId)
        {
            var userHoldings = await _context.UserHoldings.Where(s => s.Id.ToString() == userId && s.Shares != 0).ToListAsync();

            return userHoldings;
        }

        public Task<bool> LogTransaction(string userId, string stockName, int quantity)
        {
            throw new NotImplementedException();
        }

        public Task<bool> SellStock(string userId, string stockName, int quantity)
        {
            throw new NotImplementedException();
        }
    }
}
